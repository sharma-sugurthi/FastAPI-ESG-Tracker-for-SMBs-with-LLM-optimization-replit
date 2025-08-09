
"""
Workflow configuration for running the React frontend.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/frontend/start")
async def start_frontend():
    """Instructions for starting the React frontend."""
    return {
        "message": "Frontend setup instructions",
        "steps": [
            "1. Navigate to the frontend directory: cd frontend",
            "2. Install dependencies: npm install",
            "3. Start development server: npm start",
            "4. Frontend will be available at http://localhost:3000"
        ],
        "note": "Make sure your backend is running on port 5000 for API requests to work"
    }
