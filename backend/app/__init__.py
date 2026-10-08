from flask import Flask

from app.config import Config
from app.extensions import db, migrate
from app.models import Certificate, CertificateGenerationRequest, Recipient
from app.routes.certificate_routes import certificate_bp


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(certificate_bp)

    return app