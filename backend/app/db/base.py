from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    """Declarative SQLAlchemy base class."""


def create_engine_for_url(database_url: str, echo: bool = False):
    if database_url.endswith(":memory:") or database_url.endswith("sqlite://"):
        return create_engine(
            database_url,
            future=True,
            echo=echo,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(
        database_url,
        future=True,
        echo=echo,
        connect_args=connect_args,
        pool_pre_ping=True,
    )


def create_session_factory(
    database_url: str | None = None,
    *,
    echo: bool = False,
    engine=None,
) -> sessionmaker[Session]:
    if engine is None:
        if database_url is None:
            raise ValueError("database_url is required when engine is not provided")
        engine = create_engine_for_url(database_url, echo=echo)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def initialize_database(engine) -> None:
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
