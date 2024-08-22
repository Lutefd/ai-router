import asyncio
import logging
import threading
from app.grpc_server import serve as serve_grpc
from app.http_gateway import app as fastapi_app
import uvicorn
from typing import Any

logger = logging.getLogger(__name__)

class UvicornServer:
    def __init__(self, app: Any, host: str, port: int):
        self.server = uvicorn.Server(config=uvicorn.Config(app, host=host, port=port, log_level="info"))
        self.thread = threading.Thread(target=self.server.run, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self.server.should_exit = True
        self.thread.join()

async def run_servers():
    http_server = UvicornServer(fastapi_app, host="0.0.0.0", port=8000)
    http_server.start()

    grpc_task = asyncio.create_task(serve_grpc())

    try:
        await grpc_task
    except asyncio.CancelledError:
        logger.info("gRPC server task cancelled")
    except Exception as e:
        logger.error(f"Error in gRPC server: {e}")
    finally:
        logger.info("Stopping HTTP server...")
        http_server.stop()
        logger.info("HTTP server stopped")

async def main():
    servers_task = asyncio.create_task(run_servers())

    try:
        await servers_task
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    finally:
        servers_task.cancel()
        await asyncio.sleep(1)
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
