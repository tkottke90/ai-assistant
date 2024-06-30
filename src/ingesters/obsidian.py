# Reads the base directory of an Obsidian Notebook
from typing import List
from langchain.document_loaders.obsidian import ObsidianLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_core.documents.base import Document
from src.utils.string_util import checksum, stringExtractor
from src.utils.langchain import addDocumentMetadata
import re

INTERNAL_LINK = 'INTERNAL'
EXTERNAL_LINK = 'EXTERNAL'
CODE_BLOCK = 'CODE'

WIKI_LINK_REGEX=re.compile(r'\[\[([^|\]#]+)(?:#[^\]]*)?(?:\|([^\]]+))?\]\]', re.DOTALL)
EXTERNAL_LINK_REGEX = re.compile(r'[^!]?\[([^\]]+)\]\(([^\)]+)\)', re.DOTALL)
CODE_BLOCK_REGEX = re.compile(r'\`\`\`(\w*)\n([^`]*)\`\`\`', re.DOTALL)

headerSplitter = MarkdownHeaderTextSplitter([
  ("#", "h1"),
  ("##", "h2"),
  ("###", "h3"),
], strip_headers=False)

class Obsidian:

  def __init__(self, obsidianVaultPath: str, *, skipPaths: list[str] = None, apiEnabled: bool = False) -> None:
    self.vaultPath = obsidianVaultPath
    self.loader = ObsidianLoader(path=obsidianVaultPath)

    if (skipPaths is None):
      self.skipPaths = list()
    else:
      self.skipPaths = skipPaths

  def load(self):
    """Converts Obsidian documents into a list of LangChain Documents"""
    
    # Load the documents from Obsidian
    docs = list(filter(
      self.pathIsExcluded(),
      self.loader.load()
    ))

    chunks: List[Document] = list()

    # Process Each Document
    for doc in docs:
      # Calculate the checksum of the document to be used to check for changes.  This is done before
      #  extracting data so that we can detect changes made by the user as opposed to by the cleaning process
      documentChecksum = checksum(doc.page_content)

      # Get the Links from the document and replace the text with a label
      self.extractLinksToMetadata(doc, WIKI_LINK_REGEX, INTERNAL_LINK)
      self.extractLinksToMetadata(doc, EXTERNAL_LINK_REGEX, EXTERNAL_LINK)
      self.extractCodeBlocksToMetadata(doc)

      # Update the document with additional metadata for managing documents in the database
      addDocumentMetadata(doc, { "checksum": documentChecksum, "id": doc.metadata['path'] })

      # Break up document using Headers
      chunks.append([ 
        addDocumentMetadata(chunk, { "id": checksum(chunk.page_content), "path": doc.metadata['path'], "type": "DocumentChunk" })
        for chunk in headerSplitter.split_text(doc.page_content)
      ])

    return docs, chunks

  def createSequence(self, *segments: Document):
    """Creates a combined string from a sequence of LangChain Documents"""
    
    raise RuntimeError('#createSequence Not Implemented')

  def extractLinksToMetadata(self, document: Document, filter: re.Pattern, type: str):
    """Extracts a specific regex pattern from the document as a link, then updates the matched value to be just the label"""
    
    def replaceLinkWithLabel(match: re.Match[str]):
      target = match.group(0)
      label = match.group(1) if len(match.group(1)) > 0 else target

      return label

    links, updatedContent = stringExtractor(
      input=document.page_content,
      filter=filter,
      keys=['target', 'label'],
      replacementValue=replaceLinkWithLabel
    )

    for link in links:
      if len(link['label']) == 0:
        link['label'] = link['target']

    if (not 'links' in document.metadata):
      document.metadata['links'] = []

    document.metadata['links'].extend(links)
    document.page_content = updatedContent

    return document

  def extractCodeBlocksToMetadata(self, document: Document):
    document.metadata['code-blocks'] = []

    codeBlocks, updatedContent = stringExtractor(
      input=document.page_content,
      filter=CODE_BLOCK_REGEX,
      keys=['language', 'code']
    )

    document.metadata['code-blocks'] = codeBlocks
    document.page_content = updatedContent

    return document


  def pathIsExcluded(self):
    excludedPaths = [ f'{self.vaultPath}/{path}' for path in self.skipPaths ]

    def filterFn(document: Document):

      if (len(excludedPaths) == 0):
        return True

      matches = list(filter(
        lambda path: document.metadata['path'].startswith(path),
        excludedPaths
      ))

      return len(matches) == 0
    
    return filterFn
