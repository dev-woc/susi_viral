from __future__ import annotations

from fastapi import FastAPI

from app.api.dependencies import resolve_identity
from app.api import api_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.db.base import create_engine_for_url, create_session_factory, initialize_database, session_scope
from app.db.bootstrap import get_or_create_user, get_or_create_workspace
from app.services.reports.service import ReportService
from app.services.search_service import SearchService


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings.log_level)

    engine = create_engine_for_url(resolved_settings.database_url)
    session_factory = create_session_factory(engine=engine)
    initialize_database(engine)

    app = FastAPI(title=resolved_settings.app_name)
    app.include_router(api_router, prefix=resolved_settings.api_prefix)

    app.state.settings = resolved_settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.search_service = SearchService(resolved_settings, session_factory)
    app.state.report_service = ReportService(
        settings=resolved_settings,
        session_factory_override=session_factory,
    )

    with session_scope(session_factory) as session:
        workspace = get_or_create_workspace(
            session,
            slug=resolved_settings.default_workspace_slug,
            name=resolved_settings.default_workspace_name,
        )
        user = get_or_create_user(
            session,
            workspace=workspace,
            external_id=resolved_settings.default_user_external_id,
            email=resolved_settings.default_user_email,
            display_name=resolved_settings.default_user_display_name,
        )
        app.state.default_workspace = workspace
        app.state.default_user = user

    return app


app = create_app()
