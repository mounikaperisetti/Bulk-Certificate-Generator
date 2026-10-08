import time

from app import create_app
from app.extensions import db
from app.models import CertificateGenerationRequest
from app.services.generation_service import process_certificate_generation


app = create_app()


def process_pending_request():
    """Find and process the oldest pending certificate request."""

    # Pick the oldest pending request so requests are processed in order.
    certificate_request = (
        db.session.query(CertificateGenerationRequest)
        .filter_by(status="PENDING")
        .order_by(CertificateGenerationRequest.created_at.asc())
        .first()
    )

    if certificate_request is None:
        return False

    # Send the request to the service that creates the individual PDFs.
    process_certificate_generation(certificate_request.id)

    return True


def run_worker():
    """Continuously look for pending certificate generation requests."""

    print("Certificate generation worker started.")

    while True:
        with app.app_context():
            request_processed = process_pending_request()

        if not request_processed:
            # No request is waiting, so check again after a short delay.
            time.sleep(2)


if __name__ == "__main__":
    run_worker()