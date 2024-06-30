from langchain.text_splitter import SpacyTextSplitter
from langchain_core.documents.base import Document

spacySplitter = SpacyTextSplitter(
  max_length=1024,
  pipeline="en_core_web_trf"
)

def processDocument(document: Document):
  spacyDoc = spacySplitter.split_documents([document])

  


  print('====')