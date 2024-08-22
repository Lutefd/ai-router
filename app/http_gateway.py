import grpc
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Optional
from app import ai_router_pb2, ai_router_pb2_grpc

logger = logging.getLogger(__name__)

app = FastAPI()

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
