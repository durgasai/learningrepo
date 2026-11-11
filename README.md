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

When prompted, enter a topic to research. The crew produces a concise Markdown
briefing that starts with an overview, followed by a Mermaid diagram, five to
six key points, examples, and a short summary. The report is saved to `notes.md`.
The diagram uses quoted Mermaid labels so punctuation such as parentheses
doesn't break rendering.

The topic and output format are defined in `src/news_agent/config/tasks.yaml`.

## Understanding Your Crew

The news_agent Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the NewsAgent Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
