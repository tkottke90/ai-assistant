from dataclasses import dataclass, field
from src.agents.BaseAgent import BaseAgent
from src.tools.BaseTool import MyToolDict
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

prompt = ChatPromptTemplate.from_template(
    template="""


"""
)

@dataclass
class AppRouterAgent(BaseAgent):
    name = 'AppRouterAgent'
    tools: MyToolDict = field(default_factory=list)

    def invoke(input: dict, config: RunnableConfig = None):
      pass
