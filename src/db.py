import os
import functools
from langchain_core.embeddings import Embeddings
from langchain_community.chat_message_histories import Neo4jChatMessageHistory
from langchain.graphs.neo4j_graph import Neo4jGraph
from langchain.vectorstores.neo4j_vector import Neo4jVector
from typing import Protocol, Optional
from logging import Logger

NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD')
NEO4J_URL = os.environ.get('NEO4J_URL')
NEO4J_DB = os.environ.get('NEO4J_DB')


class VectorDBOptions(Protocol):
  keyword_index_name: Optional[str]
  index_name: Optional[str]
  node_label: Optional[str]
  embedding_node_property: Optional[str]
  text_node_property: Optional[str]
  logger: Optional[Logger]

class ChatHistoryOptions(Protocol):
  node_label: Optional[str]

@functools.cache
def getGraphDB():
  return Neo4jGraph(
    url=NEO4J_URL,
    database=NEO4J_DB,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD
  )

def getVectorDB(embedding: Embeddings, **kwargs: VectorDBOptions):
  return Neo4jVector(
    url=NEO4J_URL,
    database=NEO4J_DB,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    embedding=embedding,
    **kwargs
  )

def getChatHistory(userSessionId: str, **kwargs: ChatHistoryOptions):
  return Neo4jChatMessageHistory(
    url=NEO4J_URL,
    database=NEO4J_DB,
    session_id=userSessionId,
    node_label='ChatSession',
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    **kwargs
  )