from langchain.tools import tool
from duckduckgo_search import DDGS


@tool
def web_search_tool(query: str) -> str:
    """
    Searches the web for current, real-time information.
    Use this for: latest news, current prices, weather, recent events,
    sports scores, stock prices, or anything requiring up-to-date data.
    Input should be a concise search query string.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))

        if not results:
            return f"No results found for: {query}"

        output = f"Web search results for '{query}':\n\n"
        for i, r in enumerate(results, 1):
            output += f"{i}. {r.get('title', 'No title')}\n"
            output += f"   {r.get('body', 'No description')}\n"
            output += f"   Source: {r.get('href', '')}\n\n"

        return output.strip()
    except Exception as e:
        return f"Web search failed: {str(e)}"
