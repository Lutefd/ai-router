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
│   ├── __init__.py
│   ├── ai_router_pb2.py
│   ├── ai_router_pb2_grpc.py
│   ├── ai_router_pb2.pyi
│   ├── config.py
│   ├── exceptions.py
│   ├── grpc_server.py
│   └── http_gateway.py
├── docs/
│   └── architecture/
│       ├── architecture.png
│       └── architecture.mmd
├── protos/
│   └── ai_router.proto
├── .gitignore
├── config.yaml
├── docker-compose.yaml
├── Dockerfile
├── LICENSE
├── main.py
├── Makefile
├── README.md
└── requirements.txt
```

## Getting Started

1. Clone the repository:
   ```
   git clone https://github.com/lutefd/ai-router.git
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
       default_max_tokens: 4096
     anthropic:
       default_model: "claude-3-5-sonnet-20240620"
       default_max_tokens: 1024

   server:
     grpc_port: 50051
     http_port: 8080
   ```
5. Set up environment variables:
   Copyexport OPENAI_API_KEY=your_openai_api_key
   export ANTHROPIC_API_KEY=your_anthropic_api_key


6. Run the service:
   ```
   python app/main.py
   ```


## Docker Deployment

The AI Router Service is designed to be easily deployed using Docker and Docker Compose. The setup includes multiple service replicas and an Nginx load balancer for improved scalability and reliability.

### Docker Compose Commands

To deploy the service using Docker Compose:

1. Start the services:
  ```
  docker compose up --build -d
  ```
  This command builds the images if they don't exist, and starts the containers in detached mode.

2. View running containers:
  ```
   docker ps -a
  ```

3. Stop the services:
  ```
  docker compose down
  ```

### Nginx Load Balancer

The `nginx.conf` file configures Nginx as a reverse proxy and load balancer for both HTTP and gRPC traffic:

```nginx
   http {
       upstream ai-router-http {
           server ai-router:8000;
       }

       server {
           listen 80;
           location / {
               proxy_pass http://ai-router-http;
               # ... other proxy settings ...
           }
       }
   }

   stream {
       upstream ai-router-grpc {
           server ai-router:50051;
       }

       server {
           listen 8000;
           proxy_pass ai-router-grpc;
       }
   }
```

   - The `http` block handles HTTP traffic on port 80, forwarding requests to the AI Router service.
   - The `stream` block manages gRPC traffic on port 8000, directing it to the AI Router service.

### Multiple Replicas

The `docker-compose.yaml` file is configured to run multiple replicas of the AI Router service:

   ```yaml
   services:
     ai-router:
       build: .
       expose:
         - "8080"
         - "50051"
       environment:
         - OPENAI_API_KEY=${OPENAI_API_KEY}
         - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
         - GRPC_PORT=50051
         - HTTP_PORT=8080
         - CONFIG_PATH=/app/config.yaml
       volumes:
         - ./config.yaml:/app/config.yaml
       deploy:
         replicas: 3

     load-balancer:
       image: nginx:latest
       ports:
         - "80:80"   # HTTP
         - "8000:8000" # gRPC
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf:ro
       depends_on:
         - ai-router
   ```

Key points:
   - The `ai-router` service is configured with `replicas: 3`, creating three instances of the service.
   - The `load-balancer` service (Nginx) is exposed on ports 80 (HTTP) and 8000 (gRPC).
   - Nginx automatically distributes incoming requests across the three AI Router service replicas.

This setup provides several benefits:
   1. **Improved Performance**: Multiple replicas can handle more concurrent requests.
   2. **High Availability**: If one replica fails, others can continue serving requests.
   3. **Load Distribution**: Nginx balances the load across all healthy replicas.

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
