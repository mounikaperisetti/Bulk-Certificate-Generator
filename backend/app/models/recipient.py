from app.extensions import db


class Recipient(db.Model):
    """Stores recipient information for a certificate generation request."""

    __tablename__ = "recipients"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(
        db.Integer,
        db.ForeignKey("certificate_generation_requests.id"),
        nullable=False,
    )
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), nullable=False)

    request = db.relationship(
        "CertificateGenerationRequest",
        back_populates="recipients",
    )

    certificate = db.relationship(
        "Certificate",
        back_populates="recipient",
        uselist=False,
        cascade="all, delete-orphan",
    )