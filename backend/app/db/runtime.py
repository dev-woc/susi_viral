from app.core.config import get_settings
from app.db.base import create_engine_for_url, create_session_factory

settings = get_settings()
engine = create_engine_for_url(settings.database_url)
session_factory = create_session_factory(settings.database_url)
