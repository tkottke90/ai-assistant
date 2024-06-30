from langchain_core.documents.base import Document

def addDocumentMetadata(document: Document, metadata: dict):
  """Utility function for adding fields to the `metadata` dictionary in the LangChain Document instance"""
  document.metadata = dict(list(document.metadata.items()) + list(metadata.items()))
  return document

def peekMessage(input: dict):
  print(input)

  return input