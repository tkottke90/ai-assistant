from typing import Protocol
from langchain_core.documents import Document

class Ingester(Protocol):
  """Interface for a class which reads data from an external source and converts it to a knowledge graph"""

  def createSequence(self, **segments: list[Document]) -> str:
    """Creates a combined string from a sequence of LangChain Documents"""
    ...
  
  def chunk(self) -> list[Document]:
    """Generates a list of documents from the source"""
    ...