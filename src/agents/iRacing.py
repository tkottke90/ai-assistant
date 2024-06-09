from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain.output_parsers import OutputFixingParser
from src.llm import llmManager

jsonParser = JsonOutputParser()

raceSchedulerTemplate = ChatPromptTemplate.from_template(
  template="""context:
You are a AI Racing Scheduler Agent for iRacing.
Your task is to create a season schedule for a roster of drivers. 
You will be provided with a list of tracks, a list of cars, and a number of weeks to schedule.
For each week you will provide a selection of 2 track/car combinations.
Each week should be a list of two track/car combinations and the key should be "week_" plus the week number starting with 1.
The week number should be padded to 2 characters.
If possible, avoid repeating tracks across the season.
The tracks are listed by the Track Name and the Configuration Name separated by a dash.
Output your selections using the following JSON structure:

{{ "season": {{ "week_01": [{{ "track": <track_name>, "car": <car_name> }}, {{ "track": <track_name>, "car": <car_name> }}] }} }}

The assistant must return a valid JSON using a JSON Markdown block:
\```json

\```

weeks in the season: {weekCount}

tracks: {tracks}

cars: {cars}


steps:
- generate n week entries equal to the number of weeks input by the user

State each line of the steps and explain how you are completing the step.
Reminder: YOU ARE REQUIRED TO RETURN THE JSON BLOB in your response
"""
)

def JsonParserWithRetry(input: dict, config: RunnableConfig):
  try:
    return jsonParser.invoke(input, config)
  except:
    try:
      llm = llmManager.getLLM('mistral')
      jsonFixer = OutputFixingParser.from_llm(llm=llm, parser=jsonParser, max_retries=5)
      return jsonFixer.parse(input)
    except:
      # If the output fixer cant fix it, then just return
      return {}


tracks = [
  "Brands Hatch Circuit"
  "Barber Motorsports Park"
  "Summit Point Raceway"
  "Circuit de Spa-Francorchamps"
  "Tsukuba Circuit"
  "Circuit Gilles Villeneuve"
  "Sebring International Raceway"
  "Daytona International Speedway"
  "New Hampshire Motor Speedway"
  "Long Beach Street Circuit"
  "Winton Motor Raceway"
  "Silverstone Circuit"
  "Oran Park Raceway"
  "Hungaroring"
  "Charlotte Motor Speedway"
  "Phillip Island Circuit"
  "Mount Panorama Circuit"
  "Mid-Ohio Sports Car Course"
  "Fuji International Speedway"
  "Watkins Glen International"
  "Knockhill Racing Circuit"
  "Suzuka International Racing Course"
  "Donington Park Racing Circuit"
  "Red Bull Ring"
  "Road America"
  "Sandown International Motor Raceway"
  "WeatherTech Raceway at Laguna Seca"
  "Road Atlanta"
  "Oulton Park Circuit"
  "Autodromo Nazionale Monza"
  "Lime Rock Park"
  "Circuit of the Americas"
  "Okayama International Circuit"
]

configs = {
  
}

cars = [
  "Global Mozda MX-5"
  "GT4"
  "GT3"
  "GTE"
  "Radical SR8"
  "[Legacy Dallara DW12]"
  "Toyota GR86"
]

class iRacingAgent() :

  def invoke(self, input, config):
    llm = llmManager.getLLM('mistral')

    chain = raceSchedulerTemplate | llm | RunnableLambda(JsonParserWithRetry)

    chain.invoke({})