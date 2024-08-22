import yaml
from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()

class Config:
    def __init__(self):
        with open("config.yaml", "r") as config_file:
            self.config = yaml.safe_load(config_file)

        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    def get_default_model(self, provider: str) -> Optional[str]:
        return self.config.get("providers", {}).get(provider, {}).get("default_model")

config = Config()
