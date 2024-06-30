from langchain.prompts.chat import ChatPromptTemplate
from langchain.output_parsers.json import parse_and_check_json_markdown
from langchain_core.runnables import RunnableLambda
from src.interfaces.chain import Chain
from langchain.llms.base import BaseLLM

class SummarizeChain(Chain):
  verbosity: int
  summarization: str

custom_summarize_prompt = """context:
You are an AI Assistant specializing in email management.
Follow the program outlined below to review the email information.
The summary section is a collection of sentences that summarize sub-sections of the email.
The only code you should write is your response as JSON.
Do not include any comments inside of the JSON output
The assistant must return the following JSON structure:

{{ needsResponse: <boolean>, autoDelete: <boolean>, category: <category>, summary: <summary>, key_info: [<information>] }}

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

text to summarize:
{summarization}


steps:
- generate a summary of what the email is about from the summaries provided using the "summery verbosity" value on a 1 to 10 scale for how much detail to provide.  1 being a simple description and 10 being a detailed summery.
- identify key pieces of information that would help the user understand what the email is about and describe them in plain text.  For example, if the email is selling something include details about what they are selling
- select a category which best describes the email
- identify if this email requires the user to respond
- identify if this email should be deleted automatically without the user reviewing it
- return the JSON blob in your response

State each line of the steps and explain how you are completing the step.
"""

class CustomSummarizePrompt:
  
  def __init__(self, llm: BaseLLM) -> None:
    self.prompt = custom_summarize_prompt
    self.template = ChatPromptTemplate.from_template(template=self.prompt)
    self.llm = llm

  def invoke(self, chain: SummarizeChain):
    summarizeChain = self.template| self.llm | RunnableLambda(parse_and_check_json_markdown)
    return summarizeChain.invoke(chain)