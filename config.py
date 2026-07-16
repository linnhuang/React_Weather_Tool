from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()

@dataclass
class AgentConfig:
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    base_url: str = os.getenv("BASE_URL", "")
    model: str = os.getenv("MODEL", "")
    ipinfo_token: str = os.getenv("IPINFO_TOKEN", "")
    weather_api:str = os.getenv("OPENWEATHER_API_KEY", "")

    temperature: float = 0.0  # 希望模型输出严格符合我希望的样子
    max_steps: int = 6
    request_timeout: float = 60.0

    save_trajectory: bool = True
    trajectory_dir: str = "outputs/trajectories"

    max_tool_retries: int = 5
    max_observation_chars: int = 4000

EXPERIMENT_CONFIGS = {
    "no_tool": [],
    "calculator_only": ["calculator"],
    "weather_only": ["weather_tool"],
    "adress_only": ["adress_tool"],
    "date_only": ["date_tool"],
    "all_tools": [
        "calculator",
        "weather_only",
        "adress_only",
        "web_search",
    ],
}