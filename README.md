# AI Router Service

The AI Router Service is a flexible and scalable solution for routing AI requests to multiple providers, such as OpenAI and Anthropic.

## Architecture

![architecture](/docs/architecture/architecture.png)

## Features

- Support for multiple AI providers (currently OpenAI and Anthropic)
- gRPC and HTTP interfaces for client applications
- Configurable routing based on provider and model
- Extensible architecture using Repository and Strategy patterns

## Project Structure

```
ai-router/
├── app/
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── anthropic_repo.py
│   │   └── openai_repo.py
│   ├── router/
│   │   ├── __init__.py
│   │   └── router.py
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── anthropic_strategy.py
│   │   └── openai_strategy.py
│   ├── ai_router_pb2.py
│   ├── ai_router_pb2_grpc.py
│   ├── config.py
│   ├── grpc_server.py
│   ├── http_gateway.py
│   └── main.py
├── protos/
│   └── ai_router.proto
├── .gitignore
├── config.yaml
├── requirements.txt
└── README.md
```

## Getting Started

1. Clone the repository:
   ```
   git clone https://github.com/your-username/ai-router.git
   cd ai-router
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure the service by editing `config.yaml`:
   ```yaml
   providers:
     openai:
       default_model: "gpt-4o-mini"
     anthropic:
       default_model: "claude-3-5-sonnet-20240620"

   server:
     grpc_port: 50051
     http_port: 8080
   ```

5. Run the service:
   ```
   python app/main.py
   ```

## Usage

The AI Router Service can be accessed via gRPC or HTTP:

### gRPC

Use the `AIRouter` service defined in `protos/ai_router.proto`:

```protobuf
service AIRouter {
  rpc RouteRequest (AIRequest) returns (AIResponse) {}
  rpc StreamingRouteRequest (AIRequest) returns (stream AIResponse) {}
}
```

### HTTP

The HTTP gateway provides RESTful endpoints for the same functionality as the gRPC service. Refer to the API documentation for detailed usage.

## Extending the Service

To add support for a new AI provider:

1. Create a new strategy in `app/strategies/`
2. Implement the corresponding repository in `app/repositories/`
3. Update the router logic in `app/router/router.py`
4. Add the new provider configuration to `config.yaml`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
