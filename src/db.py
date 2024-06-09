import os
import functools
from langchain_core.embeddings import Embeddings
from langchain_community.chat_message_histories import Neo4jChatMessageHistory
from langchain.graphs.neo4j_graph import Neo4jGraph
from langchain.vectorstores.neo4j_vector import Neo4jVector

NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD')
NEO4J_URL = os.environ.get('NEO4J_URL')
NEO4J_DB = os.environ.get('NEO4J_DB')

@functools.cache
def getGraphDB():
  return Neo4jGraph(
    url=NEO4J_URL,
    database=NEO4J_DB,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD
  )

def getVectorDB(embedding: Embeddings):
  return Neo4jVector(
    url=NEO4J_URL,
    database=NEO4J_DB,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    embedding=embedding
  )

def getChatHistory(userSessionId: str):
  return Neo4jChatMessageHistory(
    url=NEO4J_URL,
    database=NEO4J_DB,
    session_id=userSessionId,
    node_label='ChatSession',
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD
  )