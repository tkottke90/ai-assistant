# Personal Assistant AI

As I continue to explore the space of LLM Agents and Productivity this project aims to be an implementation of what I have learned so far when working with tools like LangChain and LLMs.

Table of Contents
  - [Documentation](#documentation)
  - [Development](#development)

---
## Documentation

- [Agent Design](/design/AgentStrategy.md)

---
## Development

This application is a python application.  You will need specifically Python v3.11 to work in this repository.

### Setup: Virtual Environment

To get setup you will need to first setup virtual environment.  You can do this in a couple of ways.  In VSCode, you can use the _Python: Create Environment_ command if you have the [Python Plugin](https://marketplace.visualstudio.com/items?itemName=ms-python.python).

Then simply do CMD+SHIFT+P (CTRL+SHIFT+P on Windows) and select the option and follow the prompts.

You can also setup the environment manually:

```sh
python3.11 -m venv .venv
```

> Note that with the manual steps, you also need to activate the environment.  Checkout how your IDE recommends doing that.

### Setup: Dependencies

Once you have your virtual environment set the next step is to install all of your packages.  To do this simply run the following:

```sh
pip3 install -r requirements.txt
```

## Development: Dependencies

If you add/remove dependencies from the module, use `pipreqs` to update the requirements file

```sh
pipreqs --force
```