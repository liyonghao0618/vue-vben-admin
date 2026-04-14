from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class RiskRule(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "risk_rules"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    scene: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    priority: Mapped[int] = mapped_column(nullable=False, default=100, server_default="100")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="enabled", server_default="enabled")
    trigger_expression: Mapped[str] = mapped_column(Text, nullable=False)
    reason_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggestion_template: Mapped[str | None] = mapped_column(Text, nullable=True)


class RiskLexiconTerm(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "risk_lexicon_terms"

    term: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    scene: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="enabled", server_default="enabled")
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class PromptTemplate(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "prompt_templates"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="enabled", server_default="enabled")
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class EducationContent(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "education_contents"

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    audience: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    summary: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_body: Mapped[str] = mapped_column(Text, nullable=False)
    publish_status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", server_default="draft")
    published_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
