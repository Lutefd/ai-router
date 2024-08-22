import os
import yaml
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.load_yaml_config()
        self.load_env_config()

    def load_yaml_config(self):
        config_path = os.getenv("CONFIG_PATH", "config.yaml")
        with open(config_path, "r") as config_file:
            self.yaml_config = yaml.safe_load(config_file)

    def load_env_config(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.grpc_port = int(os.getenv("GRPC_PORT", self.yaml_config["server"]["grpc_port"]))
        self.http_port = int(os.getenv("HTTP_PORT", self.yaml_config["server"]["http_port"]))

    def get_default_model(self, provider: str) -> str:
        return os.getenv(f"{provider.upper()}_DEFAULT_MODEL",
                         self.yaml_config["providers"][provider]["default_model"])

    def get_default_max_tokens(self, provider: str) -> int:
        return int(os.getenv(f"{provider.upper()}_DEFAULT_MAX_TOKENS",
                             self.yaml_config["providers"][provider].get("default_max_tokens", 1000)))

config = Config()
