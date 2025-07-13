from hypercorn.asyncio import serve
from hypercorn.config import Config
from app import app

if __name__ == "__main__":
    config = Config()
    config.bind = ["0.0.0.0:5003"]
    import asyncio
    asyncio.run(serve(app, config))
