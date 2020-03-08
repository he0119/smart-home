from .settings import *

# Override settings if in production server.
if os.getenv('PRODUCTION_SERVER') == 'true':
    from .production import *

# Override settings if in test server.
if os.getenv('TESTING_SERVER') == 'true':
    from .testing import *
