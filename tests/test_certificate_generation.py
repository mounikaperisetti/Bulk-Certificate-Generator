from pathlib import Path
from unittest.mock import patch

import pytest

from app import create_app
from app.extensions import db
from app.models import Certificate, CertificateGenerationRequest
from app.services.generation_service import process_certificate_generation


@pytest.fixture
def app():
    """Create the Flask application using the project's MySQL database."""
    app = create_app()
    app.config.update(TESTING=True)
    return app


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    return app.test_client()


@pytest.fixture
def created_requests(app):
    """Track requests created by a test and remove them after the test."""
    request_ids = []

    yield request_ids

    with app.app_context():
        for request_id in request_ids:
            certificate_request = db.session.get(
                CertificateGenerationRequest,
                request_id,
            )

            if certificate_request is None:
                continue

            # Remove generated PDF files before deleting the database records.
            for recipient in certificate_request.recipients:
                if (
                    recipient.certificate
                    and recipient.certificate.file_path
                ):
                    Path(
                        recipient.certificate.file_path
                    ).unlink(missing_ok=True)

            db.session.delete(certificate_request)

        db.session.commit()


def create_request(client):
    """Create a small bulk certificate generation request for testing."""
    response = client.post(
        "/api/certificate-requests",
        json={
            "certificate_data": {
                "organization": "ABC Institute",
                "course_name": "Python Full Stack Development",
                "start_date": "2026-07-01",
                "end_date": "2026-09-30",
                "completion_date": "2026-10-08",
            },
            "recipients": [
                {
                    "name": "Mounika",
                    "email": "mounika@example.com",
                },
                {
                    "name": "Rahul",
                    "email": "rahul@example.com",
                },
            ],
        },
    )

    assert response.status_code == 201
    return response


def test_create_certificate_generation_request(
    client,
    created_requests,
):
    """A valid bulk request should be created and stored."""
    response = create_request(client)
    data = response.get_json()

    created_requests.append(data["request_id"])

    assert data["status"] == "PENDING"
    assert data["total_count"] == 2
    assert data["request_id"] is not None


def test_invalid_recipient_email_is_rejected(
    client,
):
    """An invalid recipient email should fail validation."""
    response = client.post(
        "/api/certificate-requests",
        json={
            "certificate_data": {
                "organization": "ABC Institute",
                "course_name": "Python Full Stack Development",
            },
            "recipients": [
                {
                    "name": "Mounika",
                    "email": "not-an-email",
                }
            ],
        },
    )

    assert response.status_code == 400

    data = response.get_json()
    assert data["message"] == "Validation failed."
    assert data["errors"]


def test_certificate_generation(
    client,
    app,
    created_requests,
):
    """A valid request should generate one completed certificate per recipient."""
    response = create_request(client)
    request_id = response.get_json()["request_id"]
    created_requests.append(request_id)

    with app.app_context():
        process_certificate_generation(request_id)

        certificate_request = db.session.get(
            CertificateGenerationRequest,
            request_id,
        )

        assert certificate_request.status == "COMPLETED"
        assert certificate_request.total_count == 2
        assert certificate_request.processed_count == 2
        assert certificate_request.success_count == 2
        assert certificate_request.failed_count == 0

        certificates = (
            db.session.query(Certificate)
            .join(Certificate.recipient)
            .filter(
                Certificate.recipient.has(
                    request_id=request_id
                )
            )
            .all()
        )

        assert len(certificates) == 2

        for certificate in certificates:
            assert certificate.status == "COMPLETED"
            assert certificate.file_path is not None
            assert Path(certificate.file_path).exists()


def test_request_status_and_progress(
    client,
    app,
    created_requests,
):
    """The request status endpoint should report generation progress."""
    response = create_request(client)
    request_id = response.get_json()["request_id"]
    created_requests.append(request_id)

    with app.app_context():
        process_certificate_generation(request_id)

    response = client.get(
        f"/api/certificate-requests/{request_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["request_id"] == request_id
    assert data["status"] == "COMPLETED"
    assert data["total_count"] == 2
    assert data["processed_count"] == 2
    assert data["success_count"] == 2
    assert data["failed_count"] == 0
    assert data["completed_at"] is not None


def test_individual_failure_does_not_stop_other_certificates(
    client,
    app,
    created_requests,
):
    """One failed certificate should not stop the remaining recipients."""
    response = create_request(client)
    request_id = response.get_json()["request_id"]
    created_requests.append(request_id)

    call_count = 0

    def generate_with_one_failure(*args, **kwargs):
        nonlocal call_count

        call_count += 1

        # Fail the first certificate deliberately.
        if call_count == 1:
            raise RuntimeError("Simulated certificate generation failure.")

        output_path = kwargs["output_path"]

        Path(output_path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        Path(output_path).write_bytes(
            b"%PDF-1.4\nSimulated certificate"
        )

    with patch(
        "app.services.generation_service.generate_certificate",
        side_effect=generate_with_one_failure,
    ):
        with app.app_context():
            process_certificate_generation(request_id)

            certificate_request = db.session.get(
                CertificateGenerationRequest,
                request_id,
            )

            assert certificate_request.status == "COMPLETED_WITH_FAILURES"
            assert certificate_request.total_count == 2
            assert certificate_request.processed_count == 2
            assert certificate_request.success_count == 1
            assert certificate_request.failed_count == 1

            certificates = (
                db.session.query(Certificate)
                .join(Certificate.recipient)
                .filter(
                    Certificate.recipient.has(
                        request_id=request_id
                    )
                )
                .order_by(Certificate.id.asc())
                .all()
            )

            assert len(certificates) == 2

            assert certificates[0].status == "FAILED"
            assert certificates[0].error_message is not None

            assert certificates[1].status == "COMPLETED"
            assert certificates[1].file_path is not None
            assert Path(certificates[1].file_path).exists()


def test_certificate_retrieval(
    client,
    app,
    created_requests,
):
    """A completed certificate should be retrievable as a PDF."""
    response = create_request(client)
    request_id = response.get_json()["request_id"]
    created_requests.append(request_id)

    with app.app_context():
        process_certificate_generation(request_id)

        certificate_request = db.session.get(
            CertificateGenerationRequest,
            request_id,
        )

        certificate = None

        for recipient in certificate_request.recipients:
            if (
                recipient.certificate
                and recipient.certificate.status == "COMPLETED"
            ):
                certificate = recipient.certificate
                break

        assert certificate is not None
        assert certificate.file_path is not None
        assert Path(certificate.file_path).exists()

        certificate_id = certificate.id

    response = client.get(
        f"/api/certificates/{certificate_id}"
    )

    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF")