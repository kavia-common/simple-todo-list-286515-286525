import json
import os

from src.api.main import app

"""
This script regenerates the OpenAPI JSON using the FastAPI application instance.

Run:
    python -m src.api.generate_openapi

Outputs:
    interfaces/openapi.json
"""

def regenerate_openapi() -> None:
    # Get the OpenAPI schema
    openapi_schema = app.openapi()

    # Write to file
    output_dir = "interfaces"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "openapi.json")

    with open(output_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)


if __name__ == "__main__":
    regenerate_openapi()
