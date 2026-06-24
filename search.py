from tavily import TavilyClient
import os

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def web_search(query):
    try:
        result = client.search(
            query=query,
            max_results=3
        )

        text = ""

        for item in result["results"]:
            text += f"""
Title: {item['title']}
Content: {item['content']}
Source: {item['url']}

"""

        return text

    except Exception as e:
        print(e)
        return ""
