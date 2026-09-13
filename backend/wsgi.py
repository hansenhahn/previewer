import os

from web import create_app
from web.config import load_settings

app = create_app(load_settings(os.environ))
