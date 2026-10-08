from pathlib import Path

from flask import Blueprint, request, send_file
from pydantic import ValidationError

from app.extensions import db
from app.models import Certificate, CertificateGenerationRequest, Recipient
from app.schemas.certificate import CertificateGenerationRequestInput

certificate_bp = Blueprint("certificate", __name__)

@certificate_bp.post("/api/certificate-requests")
def create_certificate_generation_request():
    """Create a bulk certificate generation request."""
    try:
        data = CertificateGenerationRequestInput.model_validate(request.get_json())
    except ValidationError as error:
        return {
            "message": "Validation failed.",
            "errors": error.errors(),
        }, 400

    certificate_data = data.certificate_data

    certificate_request = CertificateGenerationRequest(
        status="PENDING",
        organization=certificate_data.organization,
        course_name=certificate_data.course_name,
        start_date=certificate_data.start_date,
        end_date=certificate_data.end_date,
        completion_date=certificate_data.completion_date,
        event_name=certificate_data.event_name,
        event_date=certificate_data.event_date,
        total_count=len(data.recipients),
    )

    db.session.add(certificate_request)
    db.session.flush()

    # Store every recipient under this certificate generation request.
    for recipient_data in data.recipients:
        recipient = Recipient(
            request_id=certificate_request.id,
            name=recipient_data.name,
            email=recipient_data.email,
        )
        db.session.add(recipient)

    db.session.commit()

    return {
        "request_id": certificate_request.id,
        "status": certificate_request.status,
        "total_count": certificate_request.total_count,
        "message": "Certificate generation request created successfully.",
    }, 201
 
 
@certificate_bp.get("/api/certificate-requests/<int:request_id>")
def get_certificate_generation_request(request_id):
    """Return the current status and progress of a certificate request."""

    certificate_request = db.session.get(
        CertificateGenerationRequest,
        request_id,
    )

    if certificate_request is None:
        return {
            "message": "Certificate generation request not found."
        }, 404

    return {
        "request_id": certificate_request.id,
        "status": certificate_request.status,
        "total_count": certificate_request.total_count,
        "processed_count": certificate_request.processed_count,
        "success_count": certificate_request.success_count,
        "failed_count": certificate_request.failed_count,
        "created_at": certificate_request.created_at.isoformat(),
        "completed_at": (
            certificate_request.completed_at.isoformat()
            if certificate_request.completed_at
            else None
        ),
    }, 200
    
@certificate_bp.get("/api/certificate-requests/<int:request_id>/certificates")
def get_request_certificates(request_id):
    """Return certificate results belonging to a generation request."""

    certificate_request = db.session.get(
        CertificateGenerationRequest,
        request_id,
    )

    if certificate_request is None:
        return {
            "message": "Certificate generation request not found."
        }, 404

    certificates = []

    for recipient in certificate_request.recipients:
        certificate = recipient.certificate

        if certificate is None:
            continue

        certificates.append(
            {
                "certificate_id": certificate.id,
                "recipient_id": recipient.id,
                "name": recipient.name,
                "email": recipient.email,
                "status": certificate.status,
                "file_path": certificate.file_path,
                "error_message": certificate.error_message,
            }
        )

    return {
        "request_id": certificate_request.id,
        "status": certificate_request.status,
        "certificates": certificates,
    }, 200 

@certificate_bp.get("/api/certificates/<int:certificate_id>")
def download_certificate(certificate_id):
    """Return the generated certificate PDF for download."""

    certificate = db.session.get(Certificate, certificate_id)

    if certificate is None:
        return {
            "message": "Certificate not found."
        }, 404

    if certificate.status != "COMPLETED":
        return {
            "message": "Certificate is not available."
        }, 404

    if not certificate.file_path:
        return {
            "message": "Certificate file path is missing."
        }, 404

    file_path = Path(certificate.file_path)

    if not file_path.is_absolute():
        project_root = Path(__file__).resolve().parents[3]
        file_path = project_root / file_path

    if not file_path.exists():
        return {
            "message": "Certificate file not found."
        }, 404

    return send_file(
        file_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=file_path.name,
    )
    
    
    
   