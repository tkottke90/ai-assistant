from langchain_core.output_parsers import JsonOutputParser
from langchain.llms.base import BaseLLM
from langchain.output_parsers import RetryOutputParser
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

def JsonParserWithFixer(llm: BaseLLM):
  jsonParser = JsonOutputParser()
  fixer = RetryOutputParser.from_llm(llm=llm, parser=jsonParser)
  
  def parse(result: str):
    try:
      jsonParser.parse(result)
    except:
      fixer(result)
    
  return parse

def prompt_template_factory(prompt: str):
  return ChatPromptTemplate.from_template(template=prompt)

def prompt_factory(prompt: str):
  template = prompt_template_factory(prompt)

  def invoke(*, llm: BaseLLM, **input: dict | str):
    parseChain = template | llm

    return parseChain.invoke(input)

  return invoke


def json_prompt_factory(prompt: str):
  template = prompt_template_factory(prompt)

  def invoke(*, llm: BaseLLM, input: str):
    # parseChain = template | llm

    parseChain = { 'input': RunnablePassthrough() } | template | llm | RunnableParallel(
      input=RunnablePassthrough(),
      result=JsonParserWithFixer(llm)
    )

    return parseChain.invoke({ 'input': input })


  return invoke