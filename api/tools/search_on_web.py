from langchain.tools import tool
from ddgs import DDGS


@tool("internet_search_tool")
def internet_search_tool(query: str):
    """
    Use this when asked for general internet information
    that isn't in the database, such as current events, weather, or the stock market.
    """
    try:
        print('internet_search_tool')
        results = DDGS().text(query=query, max_results=3)
        return str(results)
    except Exception as e:
        return f"İnternet arama hatası: {str(e)}"
