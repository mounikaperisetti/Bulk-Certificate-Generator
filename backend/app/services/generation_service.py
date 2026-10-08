from datetime import datetime, timezone
from pathlib import Path

from flask import current_app

from app.extensions import db
from app.models import Certificate, CertificateGenerationRequest
from app.services.certificate_generator import generate_certificate


def process_certificate_generation(request_id):
    """Process all certificates belonging to a generation request."""

    certificate_request = db.session.get(
        CertificateGenerationRequest,
        request_id,
    )

    if certificate_request is None:
        raise ValueError(
            f"Certificate generation request {request_id} not found."
        )

    # A request should only be processed once when it is waiting.
    if certificate_request.status != "PENDING":
        return

    # Mark the request as processing before creating certificates.
    certificate_request.status = "PROCESSING"
    db.session.commit()

    # Resolve the configured storage folder from the project root
    # so certificate files are stored consistently regardless of
    # where the worker process is started from.
    project_root = Path(__file__).resolve().parents[3]
    storage_path = project_root / current_app.config["CERTIFICATE_STORAGE_PATH"]
    storage_path.mkdir(parents=True, exist_ok=True)

    # Process each recipient separately so one failure
    # does not stop the remaining certificates.
    for recipient in certificate_request.recipients:
        certificate = db.session.query(Certificate).filter_by(
            recipient_id=recipient.id
        ).first()

        if certificate is not None:
            continue

        certificate = Certificate(
            recipient_id=recipient.id,
            status="PENDING",
        )
        db.session.add(certificate)
        db.session.commit()

        try:
            # Mark this individual certificate as currently being created.
            certificate.status = "PROCESSING"
            db.session.commit()

            output_path = (
                storage_path / f"certificate_{certificate.id}.pdf"
            )

            generate_certificate(
                recipient_name=recipient.name,
                organization=certificate_request.organization,
                course_name=certificate_request.course_name,
                start_date=certificate_request.start_date,
                end_date=certificate_request.end_date,
                completion_date=certificate_request.completion_date,
                event_name=certificate_request.event_name,
                event_date=certificate_request.event_date,
                output_path=str(output_path),
            )

            # The PDF was created successfully.
            certificate.status = "COMPLETED"
            certificate.file_path = str(output_path)

            certificate_request.processed_count += 1
            certificate_request.success_count += 1

            db.session.commit()

        except Exception as error:
            # Roll back only the failed certificate transaction.
            # The next recipient should still be processed.
            db.session.rollback()

            certificate_id = certificate.id
            certificate = db.session.get(
                Certificate,
                certificate_id,
            )

            certificate.status = "FAILED"
            certificate.error_message = str(error)

            certificate_request.processed_count += 1
            certificate_request.failed_count += 1

            db.session.commit()

    # All recipients have now been attempted.
    certificate_request.completed_at = datetime.now(timezone.utc)

    if certificate_request.failed_count == 0:
        certificate_request.status = "COMPLETED"
    else:
        certificate_request.status = "COMPLETED_WITH_FAILURES"

    db.session.commit()