from fastapi import FastAPI
from typing import Dict, Any
from datetime import datetime

app = FastAPI(
    title="Simple JSON API",
    description="A simple FastAPI application returning JSON response",
    version="1.0.0",
)


@app.get("/")
def read_root() -> Dict[str, str]:
    """
    Root endpoint returning a welcome message.
    """
    return {"message": "Welcome to the FastAPI JSON endpoint!", "status": "online"}


@app.get("/api/info")
def get_info() -> Dict[str, Any]:
    """
    Endpoint returning server info and current timestamp.
    """
    return {
        "server_name": "Simple FastAPI JSON Server",
        "current_time": datetime.utcnow().isoformat(),
        "features": [
            "FastAPI framework",
            "Automatic OpenAPI documentation",
            "JSON serialization",
            "High performance",
        ],
    }


@app.get("/api/items/{item_id}")
def read_item(item_id: int, q: str = None) -> Dict[str, Any]:
    """
    Endpoint returning details for a specific item, demonstrating path and query parameters.
    """
    return {
        "item_id": item_id,
        "query_param": q,
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
    }
