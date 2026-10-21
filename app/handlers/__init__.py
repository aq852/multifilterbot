from app.handlers.admin import router as admin_router
from app.handlers.common import router as common_router
from app.handlers.indexing import router as indexing_router
from app.handlers.search import router as search_router
from app.handlers.payments import router as payments_router
from app.handlers.redeem import router as redeem_router

__all__ = ["admin_router", "common_router", "indexing_router", "payments_router", "redeem_router", "search_router"]
