from alembic import op


# revision identifiers, used by Alembic.
revision = "dee7673c0ae6"
down_revision = "5e5d6e218b93"
branch_labels = None
depends_on = None


def upgrade():
    # Rename the existing table instead of deleting it and creating a new one.
    op.rename_table(
        "generation_jobs",
        "certificate_generation_requests",
    )

    # Remove the old foreign key before renaming its column.
    op.drop_constraint(
        "recipients_ibfk_1",
        "recipients",
        type_="foreignkey",
    )

    # Rename the column so it clearly refers to a certificate request.
    op.alter_column(
        "recipients",
        "job_id",
        new_column_name="request_id",
    )

    # Connect each recipient to the renamed certificate request table.
    op.create_foreign_key(
        "fk_recipients_request_id",
        "recipients",
        "certificate_generation_requests",
        ["request_id"],
        ["id"],
    )


def downgrade():
    # Remove the new foreign key before restoring the old structure.
    op.drop_constraint(
        "fk_recipients_request_id",
        "recipients",
        type_="foreignkey",
    )

    # Restore the original column name.
    op.alter_column(
        "recipients",
        "request_id",
        new_column_name="job_id",
    )

    # Restore the original foreign key.
    op.create_foreign_key(
        "recipients_ibfk_1",
        "recipients",
        "generation_jobs",
        ["job_id"],
        ["id"],
    )

    # Restore the original table name.
    op.rename_table(
        "certificate_generation_requests",
        "generation_jobs",
    )