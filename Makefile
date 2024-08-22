# Variables
PYTHON := python
PROTO_DIR := protos
OUTPUT_DIR := app

# Phony targets
.PHONY: all clean proto

# Default target
all: proto

# Generate proto files
proto:
	$(PYTHON) -m grpc_tools.protoc \
		-I$(PROTO_DIR) \
		--python_out=$(OUTPUT_DIR) \
		--grpc_python_out=$(OUTPUT_DIR) \
		--mypy_out=$(OUTPUT_DIR) \
		$(PROTO_DIR)/ai_router.proto

# Clean generated files
clean:
	rm -f $(OUTPUT_DIR)/ai_router_pb2.py
	rm -f $(OUTPUT_DIR)/ai_router_pb2_grpc.py
	rm -f $(OUTPUT_DIR)/ai_router_pb2.pyi

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	$(PYTHON) -m unittest discover tests

# Run the application
run:
	$(PYTHON) app/main.py
