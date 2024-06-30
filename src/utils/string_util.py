import re
import hashlib
from typing import List, Callable

def checksum(input: str) -> str:
  return hashlib.md5(input.encode()).hexdigest()

def stringExtractor(*, input: str, filter: re.Pattern, keys: List[str], replacementValue: Callable[[re.Match], str] = None):
  updatedContent = str(input)
  matches = []

  if (replacementValue is None):
    replacementValue = lambda match: ""

  for groups in re.findall(filter, input):
    matches.append({ key:value for (key, value) in zip(keys, groups) })
    updatedContent = re.sub(
      filter,
      replacementValue,
      updatedContent
    )

  return matches, updatedContent


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