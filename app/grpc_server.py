# app/grpc_server.py

import grpc
import logging
from concurrent import futures
import asyncio
from . import ai_router_pb2, ai_router_pb2_grpc
from .router.router import AIRouter
from .exceptions import AIRouterException
from .config import config
from grpc_reflection.v1alpha import reflection

logger = logging.getLogger(__name__)

class AIRouterServicer(ai_router_pb2_grpc.AIRouterServicer):
    def __init__(self):
        self.router = AIRouter()

    async def RouteRequest(self, request, context):
        try:
            model = request.model if request.model else config.get_default_model(request.provider)
            response = await self.router.route_request(
                provider=request.provider,
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                model=model,
                parameters=dict(request.parameters)
            )
            return ai_router_pb2.AIResponse(
                content=response,
                provider=request.provider,
                model=model
            )
        except AIRouterException as e:
            logger.error(f"AIRouterException in RouteRequest: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return ai_router_pb2.AIResponse()
        except Exception as e:
            logger.error(f"Unexpected error in RouteRequest: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Internal server error")
            return ai_router_pb2.AIResponse()

    async def StreamingRouteRequest(self, request, context):
        try:
            model = request.model if request.model else config.get_default_model(request.provider)
            async for chunk in self.router.stream_request(
                provider=request.provider,
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                model=model,
                parameters=dict(request.parameters)
            ):
                yield ai_router_pb2.AIResponse(
                    content=chunk,
                    provider=request.provider,
                    model=model
                )
        except AIRouterException as e:
            logger.error(f"AIRouterException in StreamingRouteRequest: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in StreamingRouteRequest: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Internal server error")

async def serve():
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ('grpc.keepalive_time_ms', 10000),
            ('grpc.keepalive_timeout_ms', 5000),
            ('grpc.keepalive_permit_without_calls', True),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.http2.min_time_between_pings_ms', 10000),
            ('grpc.http2.min_ping_interval_without_data_ms', 5000),
        ]
    )
    ai_router_pb2_grpc.add_AIRouterServicer_to_server(AIRouterServicer(), server)

    SERVICE_NAMES = (
        ai_router_pb2.DESCRIPTOR.services_by_name['AIRouter'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    logger.info(f"Starting server on {listen_addr}")
    await server.start()

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        await server.stop(5)
    except Exception as e:
        logger.error(f"Unexpected error during server operation: {e}")
        await server.stop(0)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
