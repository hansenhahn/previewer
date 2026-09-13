import os

from app import create_app
from app.config import load_settings

app = create_app(load_settings(os.environ))
