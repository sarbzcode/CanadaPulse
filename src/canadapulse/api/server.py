"""Container/PaaS entry point respecting the platform's assigned port."""

import os

import uvicorn

from canadapulse.config import load_settings


def main() -> None:
    settings = load_settings()
    uvicorn.run(
        "canadapulse.api.app:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", str(settings.api_port))),
    )


if __name__ == "__main__":
    main()
