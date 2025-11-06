"""Service layer for integrations and business logic."""

from .application_path import ApplicationPathResult, discover_application_path  # noqa: F401
from .firestore_service import (  # noqa: F401
    FirestoreOpportunity,
    FirestoreProfile,
    FirestoreService,
)
from .matching import (  # noqa: F401
    MatchInsight,
    OpportunityMatch,
    build_opportunity_matches,
)
