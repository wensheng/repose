from fastapi import APIRouter, Request, HTTPException
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/github")
async def github_webhook(request: Request):
    """
    Receive GitHub webhooks.
    """
    # TODO: Verify signature using GITHUB_APP_PRIVATE_KEY or webhook secret if needed
    
    event_type = request.headers.get("X-GitHub-Event")
    if not event_type:
        raise HTTPException(status_code=400, detail="Missing X-GitHub-Event header")
    
    payload = await request.json()
    logger.info(f"Received GitHub event: {event_type}")
    
    # Simple logic to just log for now
    if event_type == "push":
        # Handle push event (e.g., trigger sync)
        repo_data = payload.get("repository", {})
        repo_full_name = repo_data.get("full_name")
        commits = payload.get("commits", [])
        
        logger.info(f"Push event for {repo_full_name}")
        
        # Agent Detection
        from app.core.agents.monitor import AgentMonitor
        from app.models.agent_event import AgentEvent
        from app.models.repository import Repository
        from app.db.session import SessionLocal
        from sqlalchemy import select
        
        monitor = AgentMonitor()
        
        # We need a db session here. For simplicity in this non-async-def route block (if it were sync) or using proper dependency injection pattern.
        # Since this is an async route, we should use a session.
        # BUT: webhooks often fire-and-forget or need fast response.
        # Ideally, we push this to Celery.
        # For Phase 3 demo, we'll do inline detection or create a background task.
        
        async with SessionLocal() as db:
             # Find repo
             # NOTE: This assumes repo exists. In real world, might need to match by full_name
             stmt = select(Repository).filter(Repository.name == repo_full_name) # simplified matching
             result = await db.execute(stmt)
             repo = result.scalars().first()
             
             if repo:
                 for commit in commits:
                     msg = commit.get("message", "")
                     detection = monitor.detect_from_commit_message(msg)
                     
                     if detection.is_agent:
                         logger.info(f"Agent detected: {detection.agent_name} in {commit.get('id')}")
                         # Record event
                         event = AgentEvent(
                             repo_id=repo.id,
                             event_type="commit",
                             agent_name=detection.agent_name,
                             confidence=detection.confidence,
                             source_ref=commit.get("id"),
                             description=f"Detected agent activity in commit: {msg}",
                             is_reviewed=False,
                             review_status="pending"
                         )
                         db.add(event)
                 await db.commit()
        
    return {"status": "received"}
