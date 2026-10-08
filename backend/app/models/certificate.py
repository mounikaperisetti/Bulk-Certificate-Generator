from datetime import datetime, timezone

from app.extensions import db


class Certificate(db.Model):
    """Stores the generation result for an individual recipient."""

    __tablename__ = "certificates"

    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(
        db.Integer,
        db.ForeignKey("recipients.id"),
        nullable=False,
        unique=True,
    )
    status = db.Column(db.String(20), nullable=False, default="PENDING")
    file_path = db.Column(db.String(500), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    recipient = db.relationship(
        "Recipient",
        back_populates="certificate",
    )