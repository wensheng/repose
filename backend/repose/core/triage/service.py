from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from repose.core.llm import LLMClient, Message
from repose.models.issue import Issue, Priority, TriageStatus

class TriageService:
    def __init__(self, db: AsyncSession, llm_client: LLMClient):
        self.db = db
        self.llm = llm_client

    async def analyze_issue(self, issue: Issue) -> Issue:
        """
        Analyze an issue using LLM to determine priority, tags, and summary.
        """
        prompt = f"""You are an automated issue triage assistant.
Analyze the following GitHub issue and provide:
1. A concise summary (max 2 sentences).
2. A priority level (LOW, MEDIUM, HIGH, CRITICAL).
3. A list of relevant tags (max 5).

Issue Title: {issue.title}
Issue Body:
{issue.body or "No description provided."}

Return your response in STRICT JSON format:
{{
  "summary": "...",
  "priority": "...",
  "tags": ["..."]
}}
"""
        messages = [Message(role="user", content=prompt)]
        
        try:
            result = await self.llm.complete(messages)
            content = result.content
            
            # Simple cleanup for JSON parsing if markdown blocks are included
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
                
            analysis = json.loads(content)
            
            # Update issue
            issue.summary = analysis.get("summary")
            
            # Map priority
            raw_prio = analysis.get("priority", "medium").lower()
            if "critical" in raw_prio: issue.priority = Priority.CRITICAL
            elif "high" in raw_prio: issue.priority = Priority.HIGH
            elif "low" in raw_prio: issue.priority = Priority.LOW
            else: issue.priority = Priority.MEDIUM
            
            issue.tags = analysis.get("tags", [])
            issue.triage_status = TriageStatus.TRIAGED
            
            await self.db.commit()
            return issue
            
        except Exception as e:
            print(f"Error analyzing issue {issue.id}: {e}")
            return issue

    async def get_pending_issues(self) -> list[Issue]:
        stmt = select(Issue).filter(Issue.triage_status == TriageStatus.PENDING)
        result = await self.db.execute(stmt)
        return result.scalars().all()
