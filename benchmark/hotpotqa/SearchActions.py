import os
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

from agentlite.actions.BaseAction import BaseAction


class WikipediaSearch(BaseAction):
    def __init__(self) -> None:
        action_name = "Wikipedia_Search"
        action_desc = "Using this API to search Wiki content."
        params_doc = {"query": "the search string. be simple."}

        super().__init__(
            action_name=action_name, action_desc=action_desc, params_doc=params_doc,
        )

    def __call__(self, query):
        # Perform a search and try candidates in order until one yields a page
        try:
            search_results = wikipedia.search(query)
        except Exception as e:
            return f"Error searching Wikipedia: {e}"

        if not search_results:
            return "No results found."

        # Try each candidate title; disable auto_suggest to avoid unexpected redirects
        for candidate in search_results:
            try:
                article = wikipedia.page(candidate, auto_suggest=False)
                return article.summary
            except DisambiguationError:
                # Ambiguous title; skip to next candidate
                continue
            except PageError:
                # This candidate didn't resolve to a page; try next
                continue
            except Exception as e:
                # Some other error (network etc.) -> return it for visibility
                return f"Error searching Wikipedia: {e}"

        # If no candidate resolved, return a helpful message with attempted titles
        return f'Could not find a valid Wikipedia page for query: "{query}" (tried: {search_results})'
