from enum import Enum
import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class SourceType(str, Enum):
    """Defines where information came from"""
    WEB = "web"
    PAPER = "paper"
    DOCUMENT = "document"
    MEMORY = "memory"
    SEED = "seed"

class SectionType(str, Enum):
    BACKGROUND = "background"
    METHODOLOGY = "methodology"
    MAIN_FINDINGS = "main_findings"
    GAP_DISCUSSION = "gap_discussion"
    CONSESUS = "consensus"
    DEBATE = "debate"
    FUTURE_DIRECTIONS = "future_directions"
    SUMMARY = "summary"

class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNDEFINED = "undefined"

class GapSeverity(str, Enum):
    CRITICAL = "critical"
    MODERATE = "moderate"
    MINOR = "minor"

class ProgressStatus(str, Enum):
    """Tracks review pipeline state. 
    The frontend can use this to show a progress bar or status indicator.
    """
    PENDING = "pending"
    PLANNING = "planning"
    RESEARCHING = "researching"
    SYNTHESIZING = "synthesizing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"
 

class Source(BaseModel):
    """Represents a piece of evidence or reference used in the review."""
    source_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    url: Optional[str] = None
    authors: Optional[list[str]] = Field(default_factory=list)
    year: Optional[int] = None
    source: SourceType
    snippet: str = ""                 # Relevant excerpt from the source
    relevance_score: float = 0.0      # Cosine similarity to the query (0-1)
    credibility_note: Optional[str] = None  # Critic agent can annotate


class ReviewSection(BaseModel):
    """A section of the review, typically written by the Synthesizer agent."""
    section_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    section_type: SectionType
    content: str
    confidence: ConfidenceLevel = ConfidenceLevel.UNDEFINED
    gap_severity: Optional[GapSeverity] = None
    sources: Optional[list[Source]] = Field(default_factory=list)
    word_count: int = 0


class KnowledgeGap(BaseModel):
    """Represents missing or weak knowledge detected by the critic."""
    gap_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    severity: GapSeverity
    suggested_queries: list[str] = Field(default_factory=list)
    supporting_source_ids: list[str] = Field(default_factory=list)
 

class AgentProgress(BaseModel):
    """Tracks actions taken by agents during the review process for observability."""
    agent_name: str
    action: str
    details: str = ""
    duration_seconds: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CriticFeedback(BaseModel):
    """Structured feedback from the Critic agent after reviewing the draft sections."""
    overall_score: float = 0.0  # Overall quality score (0-1)
    confidence_assessment: ConfidenceLevel = ConfidenceLevel.UNDEFINED
    gap_identification: list[KnowledgeGap] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)  # List of section_ids with unsupported claims
    coverage_gaps: list[str] = Field(default_factory=list)  # List of section_ids with coverage gaps
    need_retry: bool = False
    retry_instructions: Optional[str] = None  # provide instructions(prompt) for retrying the review process
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)

class ResearchContext(BaseModel):
    """Internal context object that holds all relevant data during the review process."""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query: str
    user_id: str
    subtasks: list[str] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    draft_sections: list[ReviewSection] = Field(default_factory=list)
    critic_feedback: Optional[CriticFeedback] = None
    agent_progress: list[AgentProgress] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    started_at: datetime = Field(default_factory=datetime.utcnow)
    def add_progress(self, agent_name: str, action: str, details: str = "", duration_seconds: Optional[float] = None):
        """Helper method to log agent actions in the context."""
        self.agent_progress.append(AgentProgress(
            agent_name=agent_name,
            action=action,
            details=details,
            duration_seconds=duration_seconds))
    def get_sources_by_ids(self, ids: list[str]) -> list[Source]:
        """Resolve source_ids to Source objects for a section."""
        id_set = set(ids)
        return [s for s in self.sources if s.source_id in id_set]
    
class ReviewRequest(BaseModel):
    """The input schema for initiating a review. This is what the frontend sends to the backend."""
    query: str = Field(..., description="The research question or topic to be reviewed.", min_length=10, max_length=2000)
    user_id: str = "anonymous"
    max_sources: int = Field(default=15, ge=3, le=50)
    include_traces: bool = False

class ReviewMetrics(BaseModel):
    """Observability data attached to every response."""
    total_latency_ms: int
    sources_found: int
    gaps_identified: int
    sections_written: int
    retries_used: int = 0
    coverage_score: float = 0.0   # Fraction of subtasks addressed
    confidence_score: float = 0.0   # Average confidence across sections
    overall_quality_score: float = 0.0  # Critic's overall score (0-1)

class ReviewResponse(BaseModel):
    """
    The final public response. This is the schema the frontend renders.
 
    Design note: sources are a flat list here. ReviewSection.source_ids
    are foreign keys into this list. The UI resolves them for inline
    citation display. This avoids duplicating source objects across sections.
    """
    review_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query: str
    status: ProgressStatus
    created_at: datetime = Field(default_factory=datetime.utcnow)
 
    # Core content
    sections: list[ReviewSection] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    gaps: list[KnowledgeGap] = Field(default_factory=list)

    # Quality signals (shown in the UI evaluation panel)
    overall_confidence: ConfidenceLevel = ConfidenceLevel.UNDEFINED
    coverage_score: float = 0.0        # 0-1, how much of the query was covered
 
    # Planner output (shown in the steps panel)
    subtasks: list[str] = Field(default_factory=list)
 
    # Optional — included only if ReviewRequest.include_traces == True
    agent_traces: list[AgentProgress] = Field(default_factory=list)
    critic_feedback: Optional[CriticFeedback] = None
 
    # Observability
    metrics: Optional[ReviewMetrics] = None
 
    # Error info
    error: Optional[str] = None
 
    @classmethod
    def from_context(
        cls,
        ctx: ResearchContext,
        status: ProgressStatus,
        metrics: ReviewMetrics,
        include_traces: bool = False,
    ) -> "ReviewResponse":
        """
        Build the public response from the internal ResearchContext.
        This is the only place that crosses the layer boundary.
        """
        gaps = ctx.critic_feedback.gap_identification if ctx.critic_feedback else []
        confidence = (
            ctx.critic_feedback.confidence_assessment
            if ctx.critic_feedback
            else ConfidenceLevel.UNDEFINED
        )
        return cls(
            review_id=ctx.request_id,
            query=ctx.query,
            status=status,
            sections=ctx.draft_sections,
            sources=ctx.sources,
            gaps=gaps,
            overall_confidence=confidence,
            coverage_score=metrics.coverage_score,
            subtasks=ctx.subtasks,
            agent_traces=ctx.agent_progress if include_traces else [],
            critic_feedback=ctx.critic_feedback if include_traces else None,
            metrics=metrics,
        )