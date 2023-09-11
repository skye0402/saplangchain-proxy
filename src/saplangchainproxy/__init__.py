# __init__.py

from importlib import resources
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

# Version of the sapapj-langchain-proxy package
__version__ = "0.0.2"