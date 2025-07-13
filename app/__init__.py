from quart import Quart
from dotenv import load_dotenv
import os

load_dotenv()

app = Quart(__name__)

from .api import setup_routes

setup_routes(app)
