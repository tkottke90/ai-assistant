

from typing import Callable, Optional, TypeVar


T = TypeVar('T')
U = TypeVar('U')
def findFirst(input: list[T], predicate: Callable[[T], bool]) -> Optional[T]:
  matchingItems = list(filter(
    predicate,
    input
  ))

  if (len(matchingItems) == 0):
    return None
  
  return next(iter(matchingItems))

def transform(list: list[T], predicate: Callable[[T], U]) -> list[U]:
  return [ predicate(item) for item in list  ]