import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    import ai_router_pb2
    import ai_router_pb2_grpc
except ImportError as e:
    print(f"Error importing protobuf files: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Python path: {sys.path}")
    raise
