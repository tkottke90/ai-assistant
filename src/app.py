from dataclasses import dataclass
from src.config import config
from typing import Callable, TypedDict
from src.logging import initializeLogger
from src.ingesters.obsidian import Obsidian
from langchain_core.documents.base import Document
from src.prompts.prompt_factory import json_prompt_factory
from langchain.llms.ollama import Ollama
from langsmith import Client
from src.prompts.proposition import propositionPrompt
from src.prompts.proposed_questions import proposed_question_prompt
from src.services.spaCy import processDocument
import os

client = Client()

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




# Load the documents from Obsidian
loader = Obsidian(
  obsidianVaultPath="/Users/thomaskottke/Nextcloud/Documents/Obsidian/Obsidian Notes",
  skipPaths=[
    "Templates",
    "Scripts",
    "Assets",
    "Archive"
  ]
)
documents, chunks = loader.load()

################################

QUESTION_COUNT = 10
llm = Ollama(name='mistral:7b', temperature=0.0, verbose=True)

def textRefinement(document: Document):
  # Copy original to metadata
  document.metadata['original'] = f'{document.page_content}'

  processDocument(document)

  # Questions
  # document.metadata['questions'] = proposed_question_prompt(llm=llm, input=document.page_content, question_count=QUESTION_COUNT)

  # Get Entities and Relationships

  # Get Keywords from text

  # Create a refined version of the text which 

  # print(document)
  return document

border = "=" * os.get_terminal_size().columns

def appendToFile(filename):
  def write(input: str):
    with open(filename, 'a') as file:
      print(f'Write {filename}')
      file.write(input)

  return write

def outputText(outputFn: Callable, input: str):
  outputFn(input)

outputFn = appendToFile('./var/output.txt')

lastChunk = documents[0]

outputText(outputFn, border)
outputText(outputFn, lastChunk.page_content)
outputText(outputFn, border)
outputText(outputFn, textRefinement(lastChunk))
outputText(outputFn, border)

# with open('temp.json', 'w') as f:
#   f.write(json.dumps(result, indent=2))