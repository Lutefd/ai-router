import grpc
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Optional
from app import ai_router_pb2, ai_router_pb2_grpc
from scalar_fastapi import get_scalar_api_reference
from fastapi.responses import FileResponse, JSONResponse
import yaml
from pathlib import Path
import os

logger = logging.getLogger(__name__)

app = FastAPI(openapi_url=None)

class AIRequest(BaseModel):
    provider: str
    prompt: str
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    parameters: Dict[str, str] = {}

async def get_grpc_client():
    channel = grpc.aio.insecure_channel('localhost:50051')
    return ai_router_pb2_grpc.AIRouterStub(channel)

def create_grpc_request(request: AIRequest) -> ai_router_pb2.AIRequest:

    grpc_request = ai_router_pb2.AIRequest(
        provider=request.provider,
        prompt=request.prompt,
        parameters=request.parameters
    )
    if request.max_tokens is not None:
        grpc_request.max_tokens = request.max_tokens
    if request.model is not None:
        grpc_request.model = request.model
    return grpc_request

@app.post("/generate")
async def generate(request: AIRequest):
    client = await get_grpc_client()
    try:
        grpc_request = create_grpc_request(request)
        response = await client.RouteRequest(grpc_request)
        return {
            "content": response.content,
            "provider": response.provider,
            "model": response.model
        }
    except grpc.RpcError as e:
        logger.error(f"gRPC error in generate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stream")
async def stream(request: AIRequest):
    client = await get_grpc_client()
    async def response_stream():
        try:
            grpc_request = create_grpc_request(request)
            async for response in client.StreamingRouteRequest(grpc_request):
                yield f"data: {response.content}\n\n"
        except grpc.RpcError as e:
            logger.error(f"gRPC error in stream: {e}")
            yield f"error: {str(e)}\n\n"

    return StreamingResponse(response_stream(), media_type="text/event-stream")

@app.get("/openapi.yaml", include_in_schema=False)
async def serve_openapi_yaml():
    file_path = "/app/docs/swagger/swagger.yaml"
    logger.debug(f"Attempting to serve file from: {file_path}")

    if os.path.exists(file_path):
        logger.debug(f"File found at {file_path}")
        try:
            return FileResponse(file_path, media_type="application/x-yaml")
        except Exception as e:
            logger.error(f"Error serving file: {str(e)}")
            return JSONResponse(status_code=500, content={"error": f"Error serving file: {str(e)}"})
    else:
        logger.error(f"File not found at {file_path}")
        return JSONResponse(status_code=404, content={"error": f"File not found at {file_path}"})

@app.get("/reference", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url= "/openapi.yaml",
        title=app.title,
    )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
