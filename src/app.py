from dataclasses import dataclass
from src.config import config
from typing import TypedDict
from src.logging import initializeLogger

initializeLogger()

@dataclass(kw_only=True)
class AppConfig(TypedDict):
  host: str
  port: int

config.addConfig(
  AppConfig,
  {
    'host': '0.0.0.0',
    'port': 5000
  }
)

if (config._newConfig):
  config.save()



# with open('temp.json', 'w') as f:
#   f.write(json.dumps(result, indent=2))