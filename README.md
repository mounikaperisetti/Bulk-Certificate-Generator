# Bulk Certificate Generator

A Flask-based backend application that accepts bulk certificate generation requests, validates recipient details, generates individual PDF certificates, tracks processing progress, and allows generated certificates to be retrieved.

## Features

* **Bulk requests:** Submit one request containing multiple recipients.
* **Input validation:** Validate recipient data and reject invalid email addresses.
* **PDF generation:** Generate individual PDF certificates using ReportLab.
* **Progress tracking:** Track total, processed, successful, and failed certificates.
* **Failure isolation:** Handle individual certificate-generation failures without stopping the remaining recipients.
* **Certificate retrieval:** Retrieve generated PDF certificates.
* **Persistent storage:** Store request, recipient, and certificate information in MySQL.
* **Database migrations:** Manage schema changes using Flask-Migrate and Alembic.

## Tech Stack

* **Backend:** Python, Flask
* **Validation:** Pydantic
* **Database:** MySQL
* **ORM and migrations:** Flask-SQLAlchemy, Flask-Migrate, Alembic
* **PDF generation:** ReportLab
* **Testing:** pytest

## Project Structure

```text
Bulk_Certificate_Generator/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── config.py
│   │   ├── extensions.py
│   │   └── __init__.py
│   ├── run.py
│   └── worker.py
├── migrations/
├── tests/
│   └── test_certificate_generation.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Prerequisites

* Python 3.13 or a compatible Python version
* MySQL 8.0 or compatible
* Git

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/mounikaperisetti/Bulk-Certificate-Generator.git
cd Bulk-Certificate-Generator
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure MySQL

Create a MySQL database named `bulk_certificate_db`.

Configure your `.env` file with the database connection and any other settings required by the application. Use your own local credentials, and never commit `.env` to Git.

### 5. Apply database migrations

From the project root, run:

```powershell
flask --app backend/run.py db upgrade
```

### 6. Start the application

```powershell
python backend/run.py
```

If background processing is required, run the worker in a separate terminal according to the application's worker configuration.

## Running Tests

Run the test suite from the project root:

```powershell
$env:PYTHONPATH = "backend"
pytest -v tests/test_certificate_generation.py
```

The test suite covers:

1. Certificate-generation request creation.
2. Invalid recipient email rejection.
3. Certificate generation.
4. Request status and progress tracking.
5. Individual failure isolation.
6. Certificate retrieval.

## Database Tables

* `certificate_generation_requests` — stores bulk request information and processing progress.
* `recipients` — stores recipient details associated with each request.
* `certificates` — stores certificate status, file paths, and error information.

## Security and Configuration

* Keep database credentials and other secrets in environment variables.
* Do not commit `.env`, virtual environments, or generated certificate files.
* Configure generated-file storage appropriately before deploying the application.

## Current Status

The core backend implementation is in place, and all six required tests are passing.

## Future Improvements

* A user-friendly frontend for submitting requests and tracking progress.
* A polished certificate template and design.
* Deployment configuration and production-readiness improvements.
