import base64
from dataclasses import dataclass, field
from typing import List
from src.services import EmailService, GmailService, EmailMessage
from src.llm import llmManager
from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts import PromptTemplate 
from src.agents.BaseAgent import BaseAgent
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_core.output_parsers.json import JsonOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.output_parsers import OutputFixingParser
import json # temp
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re
from ollama import generate
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.chains.summarize import load_summarize_chain
from src.prompts import image_description_prompt, custom_summarize_prompt

def stringCleanUp(chunk: str, replacers: list[tuple[str, str, re.RegexFlag]]):
  """
  A wrapper function around the 're' modules "#sub" method.  This allows us to make multiple edits to a string
  """
  output = chunk;

  for replacer in replacers:
    flags = re.NOFLAG
    if (len(replacer) == 3):
      flags = replacer[2]

    output = re.sub(replacer[0], replacer[1], output, flags=flags)

  return output

def htmlToMarkdown(html: str):
  rawMdStr = md(str(html), heading_style="ATX")
  return stringCleanUp(
    rawMdStr,
    [
      [r'\n{3,}', '\n\n'],      # Remove excessive new lines
      [r'â', '-'],              # Remove unicode character
      [r'', ''],               # Remove unicode character
      [r'\x94', '', re.UNICODE] # Remove unicode character
    ]
  )

@dataclass(kw_only=True)
class EmailProcessingState():
  subject: str = ''
  summarization: str = ''
  imageSummaries: str = ''
  summeryPrompt: str = ''
  input: str = '' # HTML String
  images: list[str] = field(default_factory=list)
  entities: list[str] = field(default_factory=list)
  categories: set[str] = field(default_factory=set)
  delete: bool = False
  relevant: bool = False
  needsResponse: bool = False
  verbosity: int = 5

gmailService = GmailService.connect('./var/client_secret.json')
emailService = EmailService(gmailService=gmailService)

jsonParser = JsonOutputParser()

def JsonParserWithRetry(input: dict, config: RunnableConfig):
  try:
    return jsonParser.invoke(input, config)
  except:
    try:
      llm = llmManager.getLLM('mistral')
      jsonFixer = OutputFixingParser.from_llm(llm=llm, parser=jsonParser, max_retries=5)
      return jsonFixer.parse(input)
    except:
      # If the output fixer cant fix it, then just return
      return {}

chunkProcessingTemplate = ChatPromptTemplate.from_template(
  template="""context:
You are an EmailAI Assistant specializing in email management.
Your task is to extract key information from the email using the steps outlined in the "program"
The only code you should write is your response as JSON.
Do not include any comments inside of the JSON output.
The assistant MUST return the following JSON structure:

{{ "summarization": "<string>", "categories": ["<categories>"], "entities": ["<entities>"], "delete": <boolean>, "relevant": <boolean> }}

The assistant must return a valid JSON using a JSON Markdown block:
\```json

\```

summery verbosity: {verbosity}

email subject:
{subject}

input:
{input}

available categories: marketing, receipt, reminder, personal, newsletter, other(<suggestion>)

steps:
- compare the subject and the input, determine if the input is related to the subject and is human readable. If it is related, set "related" to true in your response.
- if the input is not related or readable, return default values for each item and return early
- write a summery of the information provided in the input, use the "summery verbosity" value on a 1 to 10 scale for how much detail to provide.  1 being a simple description and 10 being a detailed summery.
- identify any categories that this email might fit into from the "available categories" list
- identify any entities identified in the input
- identify if the email should be automatically deleted or should be reviewed by the user
- generate a JSON response

State each line of the steps and explain how you are completing the step.
Reminder: YOU ARE REQUIRED TO RETURN THE JSON BLOB in your response
"""
)

summarizationPrompt = ChatPromptTemplate.from_template(
  template="""context:
You are an AI Assistant specializing in email management.
Follow the program outlined below to review the email information.
The summary section is a collection of sentences that summarize sub-sections of the email.
The only code you should write is your response as JSON.
Do not include any comments inside of the JSON output
The assistant must return the following JSON structure:

{{ needsResponse: <boolean>, category: <category>, summary: <summary> }}

The assistant must return the JSON using a JSON Markdown block:
\```json

\```

available categories:
- marketing
- receipt
- reminder
- personal
- newsletter
- other

summery verbosity: {verbosity}

subject: {subject}

potential categories: {categories}

summary:
{summarization}


steps:
- generate a summary of what the email is about from the summaries provided using the "summery verbosity" value on a 1 to 10 scale for how much detail to provide.  1 being a simple description and 10 being a detailed summery.
- using the potential categories identify a single category from the provided list which describes the email
- identify if this email requires the user to respond
- return the JSON blob in your response

State each line of the steps and explain how you are completing the step.
"""
)

customSummarizePrompt = ChatPromptTemplate.from_template(
  template= custom_summarize_prompt
)

imagePromptTemplate= PromptTemplate.from_template(
  template=image_description_prompt
)

RConfig = RunnableConfig | List[RunnableConfig] | None

@dataclass
class EmailAgent(BaseAgent):
  name = 'EmailAgent'

  def splitterChain(self, inputMap: EmailProcessingState, config: RConfig, **kwargs):
    llm = llmManager.getLLM('mistral')
    
    chunk_size = 500
    chunk_overlap = 30
    splitter = RecursiveCharacterTextSplitter(keep_separator=True, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    html = BeautifulSoup(inputMap.input, 'html.parser')

    images = html.findAll('images')
    # A lot of marketing emails use Tables for sections, get a list of tables from the HTML
    tables = [htmlToMarkdown(table) for table in html.find_all('table')]
    # Remove tables that are empty or just contain a header row
    tablesWithContents = [ table for table in tables if not table == '\n\n|  |\n| --- |\n\n' ]

    # docs = splitter.create_documents(tables)
    chain = chunkProcessingTemplate | llm | RunnableLambda(JsonParserWithRetry)

    response = [];
    for index,doc in enumerate(tablesWithContents):
      print(f'  > Loading Part {index + 1}/{len(tablesWithContents)}')
      response.append(
        chain.invoke(input={ 'input': doc, 'subject': inputMap.subject, 'verbosity': inputMap.verbosity })
      )

    summary = []
    entities = []
    deleteVotes = []
    categories = set()

    for chunk in response:
      if (not isinstance(chunk, dict)):
        chunk = EmailProcessingState(
          **inputMap,
          summarization=chunk,
          relevant=False
        )
      else:
        chunk = EmailProcessingState(**chunk)

      # Skip chunks the LLM has identified as irrelevant
      if (not chunk.relevant):
        continue

      deleteVotes.append(
        chunk.delete
      )

      summary.append(chunk.summarization)
      entities.extend(chunk.entities)

      for category in chunk.categories:
        inputMap.categories.add(category)

    # If more than 1/2 the chunks are marked for deletion then we assume the LLM
    # recommends deleting the email
    if (len(deleteVotes) > 0):
      inputMap.delete = (len([ vote for vote in deleteVotes if vote ]) / len(deleteVotes)) > 0.5
    else:
      inputMap.delete = True

    inputMap.summarization = '.  '.join(summary)
    inputMap.entities = entities
    inputMap.categories = list(categories)

    return inputMap

  def summarizeChain(self, input: EmailProcessingState, config: RConfig, **kwargs):
    llm = llmManager.getLLM('mistral')

    summarizeChain = summarizationPrompt | llm | RunnableLambda(JsonParserWithRetry)

    print(f'  > Summarize')
    # TODO: There is a bug here where the "result" is null.  Wrapping in a try/except to handle it for now
    try:
      result = summarizeChain.invoke(input={
        'subject': input.subject,
        'summarization': '\n'.join([input.summarization, input.imageSummaries]),
        'categories': ','.join(list(input.categories)),
        'verbosity': input.verbosity
      })

      input.summeryPrompt = summarizationPrompt.format(
        subject=input.subject,
        summarization='\n'.join([input.summarization, input.imageSummaries]),
        categories=','.join(list(input.categories)),
        verbosity=input.verbosity
      )
      input.summarization = result.get('summary', result.get('summary', input.summarization))
      input.categories = set([result.get('category')])
      input.needsResponse = result.get('needsResponse', False)
    except:
      print(f'    > Error Summarizing')

    return input

  def imageChain(self, input: EmailProcessingState, config: RConfig, **kwargs):
    def imgToBase64Str(filename):
      if (not filename):
        print('  > No Image')

      with open(filename, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')
    
    def LlavaGenerate(input: dict):
      filename = input.get('image')

      return generate(
        model="llava:13b",
        prompt=imagePromptTemplate.format(),
        images=[imgToBase64Str(filename)]
      ).get('response')

    if (len(input.images) > 0):
      print(f'  > PDF Images: {len(input.images)}')
      
      summary = []

      for img in input.images:
        print(f'    > Scan Image: {img}')
        imageChain = RunnableLambda(LlavaGenerate) | RunnableLambda(JsonParserWithRetry)

        imageResult = imageChain.invoke({ 'image': img })

        summary.append(imageResult.get('summarization'))


      reduce_template = """The following is set of summaries:
      {docs}
      Take these and distill it into a final, consolidated summary of the main themes. 
      Helpful Answer:"""
      reduce_prompt = PromptTemplate.from_template(reduce_template) | llmManager.getLLM('mistral')
      input.imageSummaries = reduce_prompt.invoke(input={ 'docs': '\n'.join(summary) })

    return input

  def invoke(self, input: dict):

    print('=== Get Emails ==')
    messages: list[EmailMessage] = emailService.getMessages('me', query='is:unread', maxResults=1)
    print(f'Emails Returned: {len(messages)}')

    print('== Analyze Email ==')
    chain = RunnableLambda(self.splitterChain) | RunnableLambda(self.imageChain) | RunnableLambda(self.summarizeChain)

    analysis: list[EmailProcessingState] = []

    custom = customSummarizePrompt | llmManager.getLLM('mistral') | RunnableLambda(JsonParserWithRetry)

    emails = []

    for message in messages:
      result = chain.invoke(input=EmailProcessingState(input=message.html, subject=message.subject, verbosity=8, images=message.images))
      emails.append({
        'summary': result['summarization'],
        'categories': list(set(result['categories'])),
        'entities': list(set(result['entities'])),
        'delete': result['delete'],
        'subject': message.subject,
        'sender': message.sender,
        'date': message.date,
        'needsResponse': result['needsResponse']
      })

    with open('./var/emailList.json', 'w') as f:
      f.write(json.dumps(emails, indent=2))

    return {}

    for index,message in enumerate(messages):
      print(f'Loading Email [{index + 1}]: {message.subject}')

      result = chain.invoke(input=EmailProcessingState(input=message.html, subject=message.subject, verbosity=8))

      analysis.append({
        'summary': result.summarization,
        'categories': list(result.categories),
        'entities': result.entities,
        'delete': result.delete,
        'subject': message.subject,
        'sender': message.sender,
        'date': message.date,
        'needsResponse': result.needsResponse
      })



    # analysis = chain.batch(inputs=[ { 'input': message.text, 'subject': message.subject } for message in messages ])

    with open('./details.json', 'w') as f:
      f.write(
        json.dumps(
          analysis,
          indent=2)
        )