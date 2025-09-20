# multiplex/settings/__init__.py
import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

env = os.getenv("DJANGO_ENV", "dev")  # default = dev

if env == "prod":
    from .prod import *
elif env == "test":
    from .test import *
else:
    from .dev import *
