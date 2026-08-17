"""
DuckDuckGo web search tool.
"""

from langchain_community.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()
search_tool.name = "search_tool"
search_tool.description = "Web search tool to find more information about a topic."
