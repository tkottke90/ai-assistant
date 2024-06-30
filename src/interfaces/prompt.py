from typing import Protocol
from langchain_core.prompts.base import BasePromptTemplate

class Prompt(Protocol):
  prompt: str
  template: BasePromptTemplate

  def invoke(input: dict):
    ...