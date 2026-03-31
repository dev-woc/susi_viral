from collections.abc import Iterator

from sqlalchemy.orm import Session

from app.db.runtime import session_factory


def get_session() -> Iterator[Session]:
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
