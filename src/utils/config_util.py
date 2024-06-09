from dotenv import find_dotenv, load_dotenv
from typing import TypedDict, TypeVar, Type, Optional
from inspect import getdoc, getmembers, signature, Parameter, get_annotations
import os
import pathlib
import yaml
import logging

# Load the .env file if one is found
load_dotenv(find_dotenv())

configLogger = logging.getLogger('Config')

ConfigSchema = TypeVar('ConfigSchema')

Config = TypedDict('Config', {
  '_schema': Optional[Type[ConfigSchema]],
  'data': ConfigSchema
});

class ConfigManager():
  version: str = 'v1'
  _configs : dict[str, Config] = {}
  _filename: str
  _newConfig: bool = False

  def __init__(self, configs: dict[str, dict], *, filename: str = None, newConfig: bool = None) -> None:
    self._configs = self.deserialize(configs)
    self._filename = filename or './var/config.yaml'
    self._newConfig = newConfig or True

    if (self._newConfig):
      configLogger.warn('Fresh configuration detected, make sure to save it')
  
  def __getitem__(self, name: str) -> ConfigSchema:
    return self._configs[name]['data']

  def deserialize(self, configs):
    return { key: { 'data': value, '_schema': None } for key,value in configs.items() }

  def serialize(self):
    return { key: value['data'] for key,value in self._configs.items() }

  def save(self):
    # Update the local config file with the values in this instance
    d = pathlib.Path(os.path.dirname(self._filename))
    if (not d.exists()):
      d.mkdir(parents=True, exist_ok=True)

    with open(self._filename, 'w') as f:
      data = self.serialize()
      yamlData = yaml.dump(data)
      f.write(yamlData)

  def from_file(filepath: str):
    d = pathlib.Path(os.path.dirname(filepath))
    if (not d.exists()):
      d.mkdir(parents=True, exist_ok=True)
    
    # Exit early of no config file exists
    if (not os.path.exists(filepath)):
      return ConfigManager({}, filename=filepath)

    # Open file and parse as YAML
    with open(filepath, 'r') as f:
      # Get file contents, returns empty string if not present
      contents: dict[str, dict] = yaml.load(f, Loader=yaml.FullLoader) or {}
      # Load the configs into a new instance
      return ConfigManager(contents, filename=filepath, newConfig=False)

  def addConfig(
    self,
    schema: Type[ConfigSchema],
    defaultValue: ConfigSchema,
    name: str = None
  ):
    name = name or schema.__name__

    if (name in self._configs):
      config = self._configs[name]

      if (config.get('_schema')):
        raise ValueError(f'Schema already registered for {name}.')

      config['_schema'] = { key:value for key,value in get_annotations(schema).items() if not key.startswith('_') }
    
      # Merge the default values with the existing config
      config['data'] = {**defaultValue, **(config.get('data') or {})}

      self._configs[name] = config
    else:
      self._configs[name] = {
        '_schema': { key:value for key,value in get_annotations(schema).items() if not key.startswith('_') },
        'data': defaultValue
      }

