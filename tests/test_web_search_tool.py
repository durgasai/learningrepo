import io
import json
import os
import unittest
from unittest.mock import patch

from news_agent.tools.web_search_tool import WebSearchTool


class _FakeResponse:
    def __init__(self, payload):
        if isinstance(payload, bytes):
            self._payload = payload
        elif isinstance(payload, str):
            self._payload = payload.encode("utf-8")
        else:
            self._payload = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class WebSearchToolTests(unittest.TestCase):
    def test_serper_results_are_formatted_with_citations(self):
        tool = WebSearchTool()
        payload = {
            "organic": [
                {
                    "title": "AI agents gain tool use",
                    "link": "https://example.com/ai-agents",
                    "snippet": "Recent agent frameworks add safer tool calling.",
                    "date": "2 days ago",
                    "source": "Example News",
                }
            ]
        }
        with patch.dict(os.environ, {"SERPER_API_KEY": "test-key"}, clear=False), patch(
            "urllib.request.urlopen", return_value=_FakeResponse(payload)
        ):
            result = tool._run("AI agents", max_results=3)

        self.assertIn('Web search results for "AI agents" (provider: serper):', result)
        self.assertIn("1. AI agents gain tool use (Example News, 2 days ago)", result)
        self.assertIn("URL: https://example.com/ai-agents", result)
        self.assertIn("Sources section", result)

    def test_duckduckgo_fallback_parses_results(self):
        tool = WebSearchTool()
        html = """
        <html><body>
          <div class="result">
            <a class="result__a" href="https://duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.org%2Fstory">Example &amp; Story</a>
            <a class="result__snippet">A <b>recent</b> development.</a>
          </div>
        </body></html>
        """
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("TAVILY_API_KEY", None)
            os.environ.pop("SERPER_API_KEY", None)
            with patch("urllib.request.urlopen", return_value=_FakeResponse(html)):
                result = tool._run("example topic", max_results=5)

        self.assertIn("(provider: duckduckgo)", result)
        self.assertIn("URL: https://example.org/story", result)
        self.assertIn("Example & Story", result)
        self.assertIn("A recent development.", result)

    def test_missing_query_returns_message(self):
        tool = WebSearchTool()
        self.assertEqual(tool._run("   "), "No query provided.")


if __name__ == "__main__":
    unittest.main()
