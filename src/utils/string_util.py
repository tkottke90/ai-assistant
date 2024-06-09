import re

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