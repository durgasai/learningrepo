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


def _quote_unquoted_mermaid_labels(markdown):
    def quote_labels(block):
        diagram = _UNQUOTED_MERMAID_NODE_PATTERN.sub(
            lambda node: f'{node.group(1)}"{node.group(2).strip()}"{node.group(3)}',
            block.group(2),
        )
        return f"{block.group(1)}{diagram}{block.group(3)}"

    return _MERMAID_BLOCK_PATTERN.sub(quote_labels, markdown)


# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    topic = input("Enter a news topic: ").strip()
    if not topic:
        raise ValueError("A news topic is required.")

    inputs = {
        'topic': topic,
        'current_year': str(datetime.now().year)
    }

    try:
        NewsAgent().crew().kickoff(inputs=inputs)
        notes_path = Path("notes.md")
        notes = notes_path.read_text(encoding="utf-8")
        notes_path.write_text(
            _quote_unquoted_mermaid_labels(notes),
            encoding="utf-8",
        )
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


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
