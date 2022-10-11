from .settings import *

# Override settings if in development server.
if os.getenv("DEVELOPMENT_SERVER") == "true":
    from .development import *

# Override settings if in production server.
if os.getenv("PRODUCTION_SERVER") == "true":
    from .production import *
