import unittest

from news_agent.main import _ensure_required_sections, _postprocess_report, _strip_outer_code_fence


class ReportPostprocessingTests(unittest.TestCase):
    def test_strip_outer_code_fence_preserves_inner_mermaid_block(self):
        markdown = (
            "```markdown\n"
            "## Overview\nIntro\n\n"
            "## Pictorial representation\n"
            "```mermaid\nflowchart TD\nA[\"X\"] --> B[\"Y\"]\n```\n"
            "```"
        )
        stripped = _strip_outer_code_fence(markdown)
        self.assertTrue(stripped.startswith("## Overview"))
        self.assertIn("```mermaid", stripped)
        self.assertNotIn("```markdown", stripped)

    def test_ensure_required_sections_adds_missing_sections_and_source_note(self):
        markdown = "## Overview\nRecent updates matter.\n\n## Sources\n- No links yet"
        result = _ensure_required_sections(markdown)

        for heading in [
            "## Overview",
            "## Pictorial representation",
            "## Key points",
            "## Examples",
            "## Risks and open questions",
            "## Summary",
            "## Sources",
        ]:
            self.assertIn(heading, result)
        self.assertIn("No source links detected", result)

    def test_postprocess_report_quotes_mermaid_and_normalizes(self):
        markdown = (
            "## Overview\nContext\n"
            "## Pictorial representation\n"
            "```mermaid\nflowchart TD\nA[Large Language Models (LLMs)] --> B[Impact]\n```\n"
            "## Key points\n- Point\n"
            "## Examples\n- Example\n"
            "## Risks and open questions\n- Risk\n"
            "## Summary\nDone\n"
            "## Sources\n- [Story — Example, 2026](https://example.com/story)\n"
        )
        result = _postprocess_report(markdown)
        self.assertIn('A["Large Language Models (LLMs)"] --> B["Impact"]', result)
        self.assertTrue(result.endswith("\n"))
        self.assertNotIn("No source links detected", result)


if __name__ == "__main__":
    unittest.main()
