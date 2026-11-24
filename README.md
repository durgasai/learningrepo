# NewsAgent Crew

Welcome to the NewsAgent Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/news_agent/config/agents.yaml` to define your agents
- Modify `src/news_agent/config/tasks.yaml` to define your tasks
- Modify `src/news_agent/crew.py` to add your own logic, tools and specific args
- Modify `src/news_agent/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ UV_NO_EDITABLE=1 crewai run
```

On this macOS setup, `UV_NO_EDITABLE=1` avoids an import failure caused by
Python ignoring the editable-install path file.

When prompted, enter a topic to research. The researcher uses a web search tool
to gather recent findings and citations, then the reporting analyst produces a
concise, decision-useful Markdown briefing with: an overview (why it matters
now), a Mermaid diagram, five to six key points (with impact and inline source
attribution), examples, risks/open questions, a short summary, and a sources
section with links. The report is saved to `notes.md`.

After generation, the app post-processes `notes.md` to quote Mermaid labels (so
punctuation such as parentheses doesn't break rendering) and to normalize
required sections/citation placeholders for a more consistent, useful report.

For best results, set a search API key in your environment (optional):
- `TAVILY_API_KEY` (preferred if available)
- `SERPER_API_KEY`

If neither is set, the agent falls back to DuckDuckGo HTML search results.

The topic and output format are defined in `src/news_agent/config/tasks.yaml`. Also `knowledge/user_preference.txt` and existing `notes.md` are sample/data files; I shouldn't modify them except if necessary - user tagged notes.md but didn't ask to regenerate it. No.

I should add unit tests for the new web search tool to verify citation-friendly formatting and provider behavior/mocking. This keeps change validated without needing LLM/network in general. I can create `tests/test_web_search_tool.py` and mock `urllib.request.urlopen` and env vars. I'll inspect how to structure tests consistent with existing unittest style. Let us write tests.

## Understanding Your Crew

The news_agent Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the NewsAgent Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
