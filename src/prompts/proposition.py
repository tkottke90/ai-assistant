from .prompt_factory import prompt_factory


propositionPrompt = prompt_factory("""You are an AI Assistant specializing in rewriting text as a list of propositions.
Your task is to rewrite the input text below using propositions
Do not include conversational text in your response.

Here is the input:
{input}
""")