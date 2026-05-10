"""
RUN SCRIPT - Start the J.A.R.V.I.S backend server
=================================================

This is the main entry point used during development.

Usage:
    python run.py

Then open:
    http://localhost:8000

Swagger Docs:
    http://localhost:8000/docs
"""

import uvicorn

# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
