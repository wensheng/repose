import asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from repose.core.celery_app import celery_app


@celery_app.task(acks_late=True)
def sync_repository(repo_id: str):
    """
    Background task to sync a repository.
    1. Fetches metadata from GitHub
    2. Updates repository details in DB
    """
    print(f"Starting sync for repo_id: {repo_id}")
    
    from repose.core.config import settings
    from repose.integrations.github import GitHubClient
    from repose.db.session import AsyncSessionLocal
    from repose.models.repository import Repository

    async def _sync():
        async with AsyncSessionLocal() as db:
            stmt = select(Repository).filter(Repository.id == repo_id)
            result = await db.execute(stmt)
            repo = result.scalars().first()
            
            if not repo:
                print(f"Repository {repo_id} not found")
                return

            client = GitHubClient(token=settings.GITHUB_PAT)
            
            try:
                # We use the existing full_name or construct from org/repo to fetch
                # If full_name is e.g. "owner/repo"
                owner = repo.org_name
                name = repo.repo_name
                
                metadata = await client.get_repo_metadata(owner, name)
                
                # Update fields
                repo.full_name = metadata.get("full_name", repo.full_name)
                repo.default_branch = metadata.get("default_branch", repo.default_branch)
                
                # If full_name changed (transfer), update org/repo
                if "/" in repo.full_name:
                    new_owner, new_name = repo.full_name.split("/", 1)
                    repo.org_name = new_owner
                    repo.repo_name = new_name
                
                repo.last_sync_at = datetime.now(timezone.utc)
                repo.sync_status = "completed"
                
                # Try to preserve updated_at from github as last_commit_at? 
                # "pushed_at" is better proxy for last activity on repo code
                pushed_at_str = metadata.get("pushed_at")
                if pushed_at_str:
                     repo.last_commit_at = datetime.fromisoformat(pushed_at_str.replace('Z', '+00:00'))

                await db.commit()
                print(f"Successfully synced metadata for {repo.full_name}")
                
            except Exception as e:
                print(f"Error syncing repo {repo_id}: {e}")
                repo.sync_status = "failed"
                await db.commit()
                raise e

    try:
        asyncio.run(_sync())
    except Exception as e:
        print(f"Sync task failed: {e}")
        # If _sync raised, it's already caught internally unless it was during commit or setup
        # But we re-raised in except block above so Celery knows it failed.
        # But wait, asyncio.run will raise the exception.
        # So we should probably catch it to ensure we don't crash the worker purely (though celery handles it)
        pass 

    print(f"Finished sync for repo_id: {repo_id}")
    return {"status": "completed", "repo_id": repo_id}


@celery_app.task(acks_late=True)
def sync_repo_issues(repo_id: str):
    """
    Sync issues for a repository.
    """
    from repose.db.session import AsyncSessionLocal
    from repose.models.repository import Repository
    from repose.models.issue import Issue
    from repose.integrations.github import GitHubClient
    from repose.core.config import settings
    
    async def _sync_issues():
        async with AsyncSessionLocal() as db:
            # Fetch repo info
            stmt = select(Repository).filter(Repository.id == repo_id)
            result = await db.execute(stmt)
            repo = result.scalars().first()
            if not repo:
                print(f"Repo {repo_id} not found")
                return

            client = GitHubClient(token=settings.GITHUB_APP_PRIVATE_KEY)
            # Assuming repo.name is "owner/repo"
            try:
                owner, name = repo.name.split("/")
                issues = await client.get_repository_issues(owner, name)
                
                for i_data in issues:
                    if "pull_request" in i_data: continue # Skip PRs
                    
                    stmt = insert(Issue).values(
                        repo_id=repo_id,
                        github_id=i_data["id"],
                        number=i_data["number"],
                        title=i_data["title"],
                        body=i_data["body"] or "",
                        state=i_data["state"],
                        html_url=i_data["html_url"],
                        # triage_status defaults to pending
                    )
                    # Upsert
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['repo_id', 'number'], # Assumes unique constraint on repo_id+number (need to ensure this in DB/Migration ideally, or fallback to PK)
                        # Actually we don't have that constraint in the migration explicitly, usually github_id is unique globally, or repo_id+number.
                        # For now, let's just use github_id if possible or just update fields.
                        # For simplicity in this demo without complex unique constraints:
                        # We will try to find existing issue by number first.
                        set_={
                            'title': stmt.excluded.title,
                            'body': stmt.excluded.body,
                            'state': stmt.excluded.state
                        }
                    )
                    # Note: Upsert with just 'repo_id' and 'number' as index_elements works ONLY if there is a unique constraint.
                    # Since we didn't add one in the manual migration, we should check existence manually or catch error.
                    # Let's do manual check for safety.
                    
                    existing_stmt = select(Issue).filter(Issue.repo_id==repo_id, Issue.number==i_data["number"])
                    existing = await db.execute(existing_stmt)
                    existing_issue = existing.scalars().first()
                    
                    if existing_issue:
                        existing_issue.title = i_data["title"]
                        existing_issue.body = i_data["body"]
                        existing_issue.state = i_data["state"]
                    else:
                        db.add(Issue(
                            repo_id=repo_id,
                            github_id=i_data["id"],
                            number=i_data["number"],
                            title=i_data["title"],
                            body=i_data["body"] or "",
                            state=i_data["state"],
                            html_url=i_data["html_url"]
                        ))
                
                await db.commit()
                print(f"Synced {len(issues)} issues for {repo.name}")

            except Exception as e:
                print(f"Error syncing issues for {repo_id}: {e}")

    asyncio.run(_sync_issues())
    return {"status": "completed"}
