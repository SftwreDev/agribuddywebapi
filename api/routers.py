from config.settings import app

from .endpoints.views import *

app.include_router(router)