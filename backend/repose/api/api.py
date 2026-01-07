from fastapi import APIRouter

from repose.api.routes import repos, webhooks, chat, agents, triage, metrics

api_router = APIRouter()
api_router.include_router(repos.router, prefix="/repos", tags=["repos"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(triage.router, prefix="/triage", tags=["triage"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
