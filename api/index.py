"""
Vercel serverless function wrapper for FastAPI application.
This routes all API requests to the FastAPI app.
"""

from backend.src.main import app

# Export the app for Vercel
__all__ = ["app"]
