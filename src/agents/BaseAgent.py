from langchain_core.runnables import Runnable
from langchain.prompts.chat import BaseMessagePromptTemplate
from ..tools.BaseTool import MyToolDict

class BaseAgent(Runnable):
  _prompt: BaseMessagePromptTemplate

  def invoke(state: dict) -> dict:
    raise NotImplementedError('#invoke method is not implemented')

  def _createToolStr(self, tools: MyToolDict):
    toolList = []

    for tool in tools:
      if (isinstance(tool, str)):
        toolList.append(f"- {tool}")
      else:
        toolList.append(tool.getToolStr())

    return '\n'.join(toolList)