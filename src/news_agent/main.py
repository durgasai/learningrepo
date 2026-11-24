#!/usr/bin/env python
import re
import sys
import warnings

from datetime import datetime
from pathlib import Path

from news_agent.crew import NewsAgent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

_MERMAID_BLOCK_PATTERN = re.compile(
    r"(```mermaid[^\n]*\n)(.*?)(\n```)", re.IGNORECASE | re.DOTALL
)
_UNQUOTED_MERMAID_NODE_PATTERN = re.compile(
    r'(\b[A-Za-z][A-Za-z0-9_]*\[)(?!["\'])([^\]\n]+)(\])'
)

_REQUIRED_SECTIONS = [
    ("## Overview", "Overview unavailable."),
    (
        "## Pictorial representation",
        "```mermaid\nflowchart TD\n    A[\"Topic\"] --> B[\"Key developments\"]\n```",
    ),
    ("## Key points", "- No key points were generated."),
    ("## Examples", "- No examples were generated."),
    ("## Risks and open questions", "- No risks or open questions were identified."),
    ("## Summary", "Summary unavailable."),
    (
        "## Sources",
        "- No sources were captured. Re-run with web search configured (e.g. `TAVILY_API_KEY` or `SERPER_API_KEY`) for cited results.",
    ),
]
_HEADING_PATTERN = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\((https?://[^)\s]+)\)")


def _quote_unquoted_mermaid_labels(markdown):
    def quote_labels(block):
        diagram = _UNQUOTED_MERMAID_NODE_PATTERN.sub(
            lambda node: f'{node.group(1)}"{node.group(2).strip()}"{node.group(3)}',
            block.group(2),
        )
        return f"{block.group(1)}{diagram}{block.group(3)}"

    return _MERMAID_BLOCK_PATTERN.sub(quote_labels, markdown)


def _strip_outer_code_fence(markdown):
    text = (markdown or "").strip()
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].strip() == "```":
        # Preserve inner fenced blocks (e.g. mermaid) by removing only outer wrapper.
        return "\n".join(lines[1:-1]).strip()
    return text


def _section_body(markdown, heading):
    pattern = re.compile(
        rf"^{re.escape(heading)}\s*$\n?(.*?)(?=^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(markdown)
    if not match:
        return None
    return match.group(1).strip()


def _ensure_required_sections(markdown):
    text = _strip_outer_code_fence(markdown or "")
    if not text:
        text = ""

    existing = {m.group(0) for m in _HEADING_PATTERN.finditer(text)}
    for heading, placeholder in _REQUIRED_SECTIONS:
        if heading in existing:
            continue
        if text and not text.endswith("\n"):
            text += "\n"
        if text:
            text += "\n"
        text += f"{heading}\n{placeholder}\n"
        existing.add(heading)

    sources_body = _section_body(text, "## Sources")
    if sources_body is not None and not _MARKDOWN_LINK_PATTERN.search(sources_body):
        note = (
            "_No source links detected in this section. Treat claims as unverified "
            "until sources are provided._"
        )
        if note not in sources_body:
            text = re.sub(
                rf"^(## Sources\s*$\n?)(.*?)(?=^##\s+|\Z)",
                lambda m: (
                    m.group(1)
                    + m.group(2).rstrip()
                    + ("\n" if m.group(2).strip() else "")
                    + f"\n{note}\n"
                ),
                text,
                flags=re.MULTILINE | re.DOTALL,
            )

    return text.strip() + "\n"


def _postprocess_report(markdown):
    text = _quote_unquoted_mermaid_labels(markdown or "")
    text = _ensure_required_sections(text)
    return text


# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def generate_notes(topic: str, output_path: str | Path = "notes.md", country: str = "") -> Path:
    """
    Run the crew for a topic (optionally focused on a country), post-process the report, and write notes.md output.
    """
    topic = (topic or "").strip()
    country = (country or "").strip()
    if not topic:
        raise ValueError("A news topic is required.")
    if not country:
        country = "Global"

    inputs = {
        'topic': topic,
        'country': country,
        'current_year': str(datetime.now().year)
    }

    notes_path = Path(output_path)
    try:
        NewsAgent().crew().kickoff(inputs=inputs)
        source_path = Path("notes.md")
        if not source_path.exists():
            raise FileNotFoundError("Crew run completed but notes.md was not created.")
        notes = source_path.read_text(encoding="utf-8")
        processed = _postprocess_report(notes)
        notes_path.write_text(processed, encoding="utf-8")
        if source_path.resolve() != notes_path.resolve():
            source_path.write_text(processed, encoding="utf-8")
        return notes_path
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}") from e


def run():
    """
    Run the crew.
    """
    topic = input("Enter a news topic: ").strip()
    generate_notes(topic)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        NewsAgent().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        NewsAgent().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        NewsAgent().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = NewsAgent().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
