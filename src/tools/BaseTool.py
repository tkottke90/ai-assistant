from dataclasses import dataclass
from inspect import Parameter, getdoc, signature
from typing import Any, Callable, List, Tuple, Union

@dataclass
class MyTool():
  name: str
  description: str
  fn: Callable
  argsDesc: List[Tuple[str, str]]

  def getToolStr(self, *, description: bool = False, args: bool = True):
    """Generates a string representation of the Tool and can be customized with flags
    
    Keyword Arguments:
    description {bool} - Include the description in the output string (default=False)
    args {bool} - Include the tool arguments in the output string (default=True)
    """
    toolStr = f"- \"{self.name}\""

    if (description):
      toolStr += f' ${self.description}'

    if (args):
      argStr = " ".join([ f"{argName}=<{argDesc}>" for (argName, argDesc) in self.argsDesc ])
      toolStr += f" {argStr}"

    return toolStr

  def __call__(self, *args: list, **kwargs: dict) -> Any:
    return self.fn(*args, **kwargs)

  def functionTool(fn: Callable = None, *, name: str = None, description: str = None, argsDesc: List[Tuple[str, str]] = None):
    """Decorator for creating MyTool instances from functions"""
    def functionWrapper(fn: Callable):
      if (argsDesc):
        args = argsDesc
      else:
        params = signature(fn).parameters
        args = ([
          (name, param.annotation) if isinstance(param.annotation, Parameter.empty) else (name, param)
          for name, param
          in params.items()
        ])

      tool = MyTool(
        name=name if isinstance(name, str) else fn.__name__,
        description=description if isinstance(description, str) else getdoc(fn),
        fn=fn,
        argsDesc=args
      )
      
      return tool
    
    if (isinstance(fn, Callable) or isinstance(fn, MyTool)):
      return functionWrapper(fn)
    else:
      return functionWrapper

MyToolDict = List[Union[str, MyTool]]
"""Custom type for representing a list of tools"""