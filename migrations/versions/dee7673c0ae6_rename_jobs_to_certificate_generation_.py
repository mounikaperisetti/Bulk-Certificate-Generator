from alembic import op
import sqlalchemy as sa

revision = "dee7673c0ae6"
down_revision = "5e5d6e218b93"
branch_labels = None
depends_on = None
def upgrade():
    op.rename_table(
    "generation_jobs",
    "certificate_generation_requests",

    )


op.drop_constraint(
    "recipients_ibfk_1",
    "recipients",
    type_="foreignkey",
)

op.alter_column(
    "recipients",
    "job_id",
    new_column_name="request_id",
    existing_type=sa.Integer(),
)

op.create_foreign_key(
    "fk_recipients_request_id",
    "recipients",
    "certificate_generation_requests",
    ["request_id"],
    ["id"],
)


def downgrade():
    op.drop_constraint(
    "fk_recipients_request_id",
    "recipients",
    type_="foreignkey",
    )


op.alter_column(
    "recipients",
    "request_id",
    new_column_name="job_id",
    existing_type=sa.Integer(),
)

op.create_foreign_key(
    "recipients_ibfk_1",
    "recipients",
    "generation_jobs",
    ["job_id"],
    ["id"],
)

op.rename_table(
    "certificate_generation_requests",
    "generation_jobs",
)
