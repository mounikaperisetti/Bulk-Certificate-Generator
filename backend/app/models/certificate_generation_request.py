from datetime import datetime, timezone

from app.extensions import db


class CertificateGenerationRequest(db.Model):
    """Stores a bulk certificate generation request and its progress."""

    __tablename__ = "certificate_generation_requests"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(30), nullable=False, default="PENDING")

    organization = db.Column(db.String(255), nullable=True)
    course_name = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    completion_date = db.Column(db.Date, nullable=True)
    event_name = db.Column(db.String(255), nullable=True)
    event_date = db.Column(db.Date, nullable=True)

    total_count = db.Column(db.Integer, nullable=False)
    processed_count = db.Column(db.Integer, nullable=False, default=0)
    success_count = db.Column(db.Integer, nullable=False, default=0)
    failed_count = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at = db.Column(db.DateTime, nullable=True)

    # A request contains all recipients whose certificates need to be created.
    recipients = db.relationship(
        "Recipient",
        back_populates="request",
        cascade="all, delete-orphan",
    )