import unittest

from news_agent.main import _quote_unquoted_mermaid_labels


class MermaidFormattingTests(unittest.TestCase):
    def test_quotes_unquoted_labels_in_mermaid_blocks(self):
        markdown = (
            "```mermaid\n"
            "flowchart TD\n"
            "    A[Large Language Models (LLMs)] --> B[Multimodal Capabilities]\n"
            "```"
        )

        result = _quote_unquoted_mermaid_labels(markdown)

        self.assertIn(
            'A["Large Language Models (LLMs)"] --> B["Multimodal Capabilities"]',
            result,
        )

    def test_leaves_quoted_labels_and_regular_markdown_unchanged(self):
        markdown = (
            "Text with A[not a diagram]\n"
            "```mermaid\n"
            'flowchart TD\n    A["Quoted Label"] --> B["Another Label"]\n'
            "```"
        )

        self.assertEqual(_quote_unquoted_mermaid_labels(markdown), markdown)


if __name__ == "__main__":
    unittest.main()
