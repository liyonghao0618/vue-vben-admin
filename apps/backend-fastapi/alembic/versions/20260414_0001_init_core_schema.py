"""init core schema"""

from alembic import op
import sqlalchemy as sa


revision = "20260414_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_configs",
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("group", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_system_configs_group"), "system_configs", ["group"], unique=False)
    op.create_index(op.f("ix_system_configs_key"), "system_configs", ["key"], unique=True)

    op.create_table(
        "education_contents",
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("audience", sa.String(length=30), nullable=False),
        sa.Column("summary", sa.String(length=255), nullable=True),
        sa.Column("cover_image_url", sa.String(length=255), nullable=True),
        sa.Column("content_body", sa.Text(), nullable=False),
        sa.Column("publish_status", sa.String(length=20), server_default="draft", nullable=False),
        sa.Column("published_at", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_education_contents_audience"), "education_contents", ["audience"], unique=False)
    op.create_index(op.f("ix_education_contents_category"), "education_contents", ["category"], unique=False)

    op.create_table(
        "prompt_templates",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="enabled", nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_prompt_templates_category"), "prompt_templates", ["category"], unique=False)
    op.create_index(op.f("ix_prompt_templates_code"), "prompt_templates", ["code"], unique=True)

    op.create_table(
        "risk_lexicon_terms",
        sa.Column("term", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("scene", sa.String(length=20), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="enabled", nullable=False),
        sa.Column("source", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_risk_lexicon_terms_category"), "risk_lexicon_terms", ["category"], unique=False)
    op.create_index(op.f("ix_risk_lexicon_terms_scene"), "risk_lexicon_terms", ["scene"], unique=False)
    op.create_index(op.f("ix_risk_lexicon_terms_term"), "risk_lexicon_terms", ["term"], unique=False)

    op.create_table(
        "risk_rules",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("scene", sa.String(length=20), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("priority", sa.Integer(), server_default="100", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="enabled", nullable=False),
        sa.Column("trigger_expression", sa.Text(), nullable=False),
        sa.Column("reason_template", sa.Text(), nullable=True),
        sa.Column("suggestion_template", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_risk_rules_code"), "risk_rules", ["code"], unique=True)
    op.create_index(op.f("ix_risk_rules_scene"), "risk_rules", ["scene"], unique=False)

    op.create_table(
        "roles",
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_system", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_roles_code"), "roles", ["code"], unique=True)

    op.create_table(
        "users",
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("last_login_at", sa.String(length=40), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_phone"), "users", ["phone"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "call_recognition_records",
        sa.Column("elder_user_id", sa.String(length=36), nullable=False),
        sa.Column("caller_number", sa.String(length=30), nullable=True),
        sa.Column("transcript_text", sa.Text(), nullable=True),
        sa.Column("transcript_summary", sa.Text(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("risk_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("hit_rule_codes", sa.Text(), nullable=True),
        sa.Column("hit_terms", sa.Text(), nullable=True),
        sa.Column("analysis_summary", sa.Text(), nullable=True),
        sa.Column("suggestion_action", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["elder_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_call_recognition_records_elder_user_id"), "call_recognition_records", ["elder_user_id"], unique=False)
    op.create_index(op.f("ix_call_recognition_records_risk_level"), "call_recognition_records", ["risk_level"], unique=False)

    op.create_table(
        "elder_family_bindings",
        sa.Column("elder_user_id", sa.String(length=36), nullable=False),
        sa.Column("family_user_id", sa.String(length=36), nullable=False),
        sa.Column("relationship_type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("is_emergency_contact", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("authorized_at", sa.String(length=40), nullable=True),
        sa.Column("revoked_at", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["elder_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["family_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("elder_user_id", "family_user_id", name="uq_elder_family_bindings_pair"),
    )
    op.create_index(op.f("ix_elder_family_bindings_elder_user_id"), "elder_family_bindings", ["elder_user_id"], unique=False)
    op.create_index(op.f("ix_elder_family_bindings_family_user_id"), "elder_family_bindings", ["family_user_id"], unique=False)

    op.create_table(
        "risk_alerts",
        sa.Column("elder_user_id", sa.String(length=36), nullable=False),
        sa.Column("source_type", sa.String(length=20), nullable=False),
        sa.Column("source_record_id", sa.String(length=36), nullable=True),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("risk_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("summary", sa.String(length=255), nullable=False),
        sa.Column("reason_detail", sa.Text(), nullable=True),
        sa.Column("suggestion_action", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="new", nullable=False),
        sa.Column("occurred_at", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["elder_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_risk_alerts_elder_user_id"), "risk_alerts", ["elder_user_id"], unique=False)
    op.create_index(op.f("ix_risk_alerts_risk_level"), "risk_alerts", ["risk_level"], unique=False)
    op.create_index(op.f("ix_risk_alerts_source_type"), "risk_alerts", ["source_type"], unique=False)

    op.create_table(
        "sms_recognition_records",
        sa.Column("elder_user_id", sa.String(length=36), nullable=False),
        sa.Column("sender", sa.String(length=50), nullable=True),
        sa.Column("message_text", sa.Text(), nullable=False),
        sa.Column("masked_message_text", sa.Text(), nullable=True),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("risk_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("hit_rule_codes", sa.Text(), nullable=True),
        sa.Column("hit_terms", sa.Text(), nullable=True),
        sa.Column("analysis_summary", sa.Text(), nullable=True),
        sa.Column("suggestion_action", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["elder_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sms_recognition_records_elder_user_id"), "sms_recognition_records", ["elder_user_id"], unique=False)
    op.create_index(op.f("ix_sms_recognition_records_risk_level"), "sms_recognition_records", ["risk_level"], unique=False)

    op.create_table(
        "user_role_links",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("role_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_role_links_user_role"),
    )

    op.create_table(
        "notification_records",
        sa.Column("alert_id", sa.String(length=36), nullable=False),
        sa.Column("receiver_user_id", sa.String(length=36), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("notification_type", sa.String(length=30), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("read_at", sa.String(length=40), nullable=True),
        sa.Column("sent_at", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["alert_id"], ["risk_alerts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["receiver_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notification_records_alert_id"), "notification_records", ["alert_id"], unique=False)
    op.create_index(op.f("ix_notification_records_receiver_user_id"), "notification_records", ["receiver_user_id"], unique=False)

    op.create_table(
        "workorders",
        sa.Column("alert_id", sa.String(length=36), nullable=False),
        sa.Column("elder_user_id", sa.String(length=36), nullable=False),
        sa.Column("assigned_to_user_id", sa.String(length=36), nullable=True),
        sa.Column("workorder_no", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("priority", sa.String(length=20), server_default="medium", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("dispose_method", sa.String(length=30), nullable=True),
        sa.Column("dispose_result", sa.Text(), nullable=True),
        sa.Column("closed_at", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["alert_id"], ["risk_alerts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assigned_to_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["elder_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workorders_alert_id"), "workorders", ["alert_id"], unique=False)
    op.create_index(op.f("ix_workorders_elder_user_id"), "workorders", ["elder_user_id"], unique=False)
    op.create_index(op.f("ix_workorders_workorder_no"), "workorders", ["workorder_no"], unique=True)

    op.create_table(
        "workorder_actions",
        sa.Column("workorder_id", sa.String(length=36), nullable=False),
        sa.Column("operator_user_id", sa.String(length=36), nullable=True),
        sa.Column("action_type", sa.String(length=30), nullable=False),
        sa.Column("from_status", sa.String(length=20), nullable=True),
        sa.Column("to_status", sa.String(length=20), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["operator_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["workorder_id"], ["workorders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workorder_actions_operator_user_id"), "workorder_actions", ["operator_user_id"], unique=False)
    op.create_index(op.f("ix_workorder_actions_workorder_id"), "workorder_actions", ["workorder_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_system_configs_key"), table_name="system_configs")
    op.drop_index(op.f("ix_system_configs_group"), table_name="system_configs")
    op.drop_table("system_configs")
    op.drop_index(op.f("ix_workorder_actions_workorder_id"), table_name="workorder_actions")
    op.drop_index(op.f("ix_workorder_actions_operator_user_id"), table_name="workorder_actions")
    op.drop_table("workorder_actions")
    op.drop_index(op.f("ix_workorders_workorder_no"), table_name="workorders")
    op.drop_index(op.f("ix_workorders_elder_user_id"), table_name="workorders")
    op.drop_index(op.f("ix_workorders_alert_id"), table_name="workorders")
    op.drop_table("workorders")
    op.drop_index(op.f("ix_notification_records_receiver_user_id"), table_name="notification_records")
    op.drop_index(op.f("ix_notification_records_alert_id"), table_name="notification_records")
    op.drop_table("notification_records")
    op.drop_table("user_role_links")
    op.drop_index(op.f("ix_sms_recognition_records_risk_level"), table_name="sms_recognition_records")
    op.drop_index(op.f("ix_sms_recognition_records_elder_user_id"), table_name="sms_recognition_records")
    op.drop_table("sms_recognition_records")
    op.drop_index(op.f("ix_risk_alerts_source_type"), table_name="risk_alerts")
    op.drop_index(op.f("ix_risk_alerts_risk_level"), table_name="risk_alerts")
    op.drop_index(op.f("ix_risk_alerts_elder_user_id"), table_name="risk_alerts")
    op.drop_table("risk_alerts")
    op.drop_index(op.f("ix_elder_family_bindings_family_user_id"), table_name="elder_family_bindings")
    op.drop_index(op.f("ix_elder_family_bindings_elder_user_id"), table_name="elder_family_bindings")
    op.drop_table("elder_family_bindings")
    op.drop_index(op.f("ix_call_recognition_records_risk_level"), table_name="call_recognition_records")
    op.drop_index(op.f("ix_call_recognition_records_elder_user_id"), table_name="call_recognition_records")
    op.drop_table("call_recognition_records")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_phone"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_roles_code"), table_name="roles")
    op.drop_table("roles")
    op.drop_index(op.f("ix_risk_rules_scene"), table_name="risk_rules")
    op.drop_index(op.f("ix_risk_rules_code"), table_name="risk_rules")
    op.drop_table("risk_rules")
    op.drop_index(op.f("ix_risk_lexicon_terms_term"), table_name="risk_lexicon_terms")
    op.drop_index(op.f("ix_risk_lexicon_terms_scene"), table_name="risk_lexicon_terms")
    op.drop_index(op.f("ix_risk_lexicon_terms_category"), table_name="risk_lexicon_terms")
    op.drop_table("risk_lexicon_terms")
    op.drop_index(op.f("ix_prompt_templates_code"), table_name="prompt_templates")
    op.drop_index(op.f("ix_prompt_templates_category"), table_name="prompt_templates")
    op.drop_table("prompt_templates")
    op.drop_index(op.f("ix_education_contents_category"), table_name="education_contents")
    op.drop_index(op.f("ix_education_contents_audience"), table_name="education_contents")
    op.drop_table("education_contents")
