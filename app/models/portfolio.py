# app/models/portfolio.py

import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import ( Column, 
                        String,
                        Boolean,
                        DateTime,
                        Index,
                    )

from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.adapters.database import Base


class Portfolio(Base):

    """
    Represents a generated portfolio configuration.

    This table stores:
    - User metadata
    - Generated portfolio content (JSON)
    - Deployment status
    """

    __tablename__ = "portfolios"

   
    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Identifiers
    # user_id as str is fine for now; can be changed to UUID later when auth is added
    user_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
        doc="Identifier of the user who owns this portfolio",
    )

    job_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        index=True,
        doc="Background job ID used for generation tracking",
    )

    # User Metadata
    full_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    email: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

 
    # Portfolio Content
    content: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        doc="Full generated portfolio JSON payload",
    )

    # Theme & Deployment
    theme_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="modern_tech",
    )

    deployed_url: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        doc="Public URL after deployment",
    )

    is_published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

# Indexes
Index("ix_portfolios_user_id", Portfolio.user_id)
Index("ix_portfolios_job_id", Portfolio.job_id)
