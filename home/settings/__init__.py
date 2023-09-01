import os

from .settings import *  # noqa: F403

# Override settings if in development server.
if os.getenv("DEVELOPMENT_SERVER") == "true":
    from .development import *  # noqa: F403

# Override settings if in production server.
if os.getenv("PRODUCTION_SERVER") == "true":
    from .production import *  # noqa: F403
