"""MCP (Model Context Protocol) router for AI agent tools."""

from fastapi import APIRouter

# Import all MCP tool routers
from .add_task import router as add_task_router
from .list_tasks import router as list_tasks_router
from .get_task import router as get_task_router
from .update_task import router as update_task_router
from .delete_task import router as delete_task_router
from .restore_task import router as restore_task_router
from .complete_task import router as complete_task_router

router = APIRouter(prefix="/mcp", tags=["mcp"])

# Include all MCP tool routers
router.include_router(add_task_router)
router.include_router(list_tasks_router)
router.include_router(get_task_router)
router.include_router(update_task_router)
router.include_router(delete_task_router)
router.include_router(restore_task_router)
router.include_router(complete_task_router)