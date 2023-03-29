
import uvicorn

from api.routers import *
from config.settings import app

app = app

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, debug=True)
