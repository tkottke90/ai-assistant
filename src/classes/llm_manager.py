from dataclasses import dataclass, field
from langchain.llms.base import BaseLLM
from langchain.embeddings.base import Embeddings
from typing import TypedDict
from src.config import config
from langchain.llms.openai import OpenAIChat
from langchain.llms.ollama import Ollama
from enum import Enum, auto
from langsmith import Client

class LLM_ENGINE(Enum):
  Ollama = auto()
  OpenAI = auto()


ENGINE_MAP: dict[LLM_ENGINE, BaseLLM] = {
  LLM_ENGINE.Ollama.value: Ollama,
  LLM_ENGINE.OpenAI.value: OpenAIChat
}

LLM_Config = TypedDict('LLM_Config', {
  'engine': LLM_ENGINE,
  'name': str,
  'model': str,
  'temperature': int,
  'verbose': bool
})

@dataclass(kw_only=True)
class Manager_Config(TypedDict):
  langsmith: bool = field(default=False)
  engines: dict[str, dict] = field(default_factory=dict)
  llms: list[str, LLM_Config] = field(default_factory=dict)
  embeddings: list[str, LLM_Config] = field(default_factory=dict)
  verbose: bool = field(default=False)
  defaultLLM: str = field(default='')
  defaultEmbedding: str = field(default='')

config.addConfig(Manager_Config, {
  'langsmith': False,
  'engines': {},
  'llms': [
    {
      'name': 'llama2',
      'model': 'llama2',
      'verbose': True,
      'engine': LLM_ENGINE.Ollama.value,
      'temperature': 10
    }
  ],
  'embeddings': [
    {
      'name': 'llama2',
      'model': 'llama2',
      'verbose': True,
      'engine': LLM_ENGINE.Ollama.value,
      'temperature': 10
    }
  ],
  'verbose': False,
  'defaultLLM': '',
  'defaultEmbedding': ''
}, 'LLM_Config')

class LLM_Manager():
  _langsmithClient: Client
  _llms: dict[str, BaseLLM] = {}
  _embeddings:  dict[str, Embeddings] = {}

  _defaultLLM: BaseLLM = None
  _defaultEmbedding: Embeddings = None
  
  def __init__(self, config: Manager_Config) -> None:
    llmConfig: list[LLM_Config] = config['llms']

    if ('langsmith' in config and config['langsmith'] == True):
      self._langsmithClient = Client()

    # Configure LLMs
    for value in llmConfig:
      llmEngine = ENGINE_MAP[value['engine']]

      # TODO make llmEngine a function which optionally allows us to configure model validation to avoid runtime errors

      self._llms.update({
        value['name']: llmEngine(
          model=value['model'],
          temperature=value['temperature'],
          verbose=value['verbose']
        )
      })

      if (value['name'] == config['defaultLLM']):
        self._defaultLLM = self._llms[value['name']]

      if (self._defaultLLM == None):
        self._defaultLLM = self._llms[value['name']]

  def getLLM(self, name: str):
    return self._llms.get(name, self._defaultLLM)

  def getEmbedding(name: str):
    pass


  def from_config():
    storedConfig = config['LLM_Config']

    return LLM_Manager({ **storedConfig })
