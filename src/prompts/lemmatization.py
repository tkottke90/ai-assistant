from .prompt_factory import prompt_factory

proposed_question_prompt = prompt_factory(
  """You are an AI Assistant specializing computational linguistics.
Your your task is to rewrite the .
You will generate {question_count} question/answer pairs.
Do not include conversational text in your response.
Return your response using the following JSON structure:

{{ "questions": [ {{ "question": <question>, "answer": <answer> }} ] }}

The assistant must return a valid JSON using a JSON Markdown block:
\```json

\```

Here is the input text:
{input}
"""
)