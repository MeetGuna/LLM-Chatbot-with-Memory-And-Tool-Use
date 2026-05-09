from langchain.tools import tool
import wikipedia


@tool
def wiki_tool(query: str) -> str:
    """
    Fetches a summary from Wikipedia.
    Use this for: definitions, historical facts, famous people, places,
    scientific concepts, companies, technologies, and general knowledge.
    Input should be the topic or entity to look up.
    """
    try:
        # Search for the best matching article
        search_results = wikipedia.search(query, results=3)
        if not search_results:
            return f"No Wikipedia article found for: {query}"

        # Try to get the summary of the top result
        for title in search_results:
            try:
                summary = wikipedia.summary(title, sentences=4, auto_suggest=False)
                page = wikipedia.page(title, auto_suggest=False)
                return (
                    f"Wikipedia: {page.title}\n\n"
                    f"{summary}\n\n"
                    f"Read more: {page.url}"
                )
            except wikipedia.DisambiguationError as e:
                # Pick the first option
                try:
                    summary = wikipedia.summary(e.options[0], sentences=4)
                    return f"Wikipedia: {e.options[0]}\n\n{summary}"
                except Exception:
                    continue
            except Exception:
                continue

        return f"Could not retrieve Wikipedia content for: {query}"
    except Exception as e:
        return f"Wikipedia lookup failed: {str(e)}"
