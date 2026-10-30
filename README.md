# Iota Agent

A tool-calling AI agent built with the Anthropic API and Streamlit. Claude decides
when a tool is needed, the app runs that tool locally, and the chat UI shows every
tool step (which tool, what input, what result) before the final answer.

## Live Demo

[Click here for live demo](https://iota-agent.streamlit.app/)

## Why this project

Iota (chatbot) and the RAG app answer questions. An agent goes one step further:
it can request actions. This project is a small, working example of that loop, built
to understand how tool calling works end to end rather than to be feature-complete.

## How it works

1. The user's message is sent to Claude together with the tool definitions.
2. Claude reads each tool's name and description and decides: answer directly, or request a tool.
3. If it requests a tool, the response has `stop_reason == "tool_use"`. Claude does not run anything itself; it only names the tool and its inputs.
4. The app runs the matching Python function locally.
5. The result is sent back to Claude as a `tool_result`, linked to the original request by its `tool_use_id`.
6. Claude writes the final answer in natural language.
7. The UI shows a tool bubble (tool, input, result) followed by the answer bubble.

```
User -> Claude (with tools) -> tool request -> local function -> result -> Claude -> answer
```

Tool turns cost two API calls; turns without a tool cost one.

## Tools

- **`math_calculations`**: evaluates an arithmetic expression. Square roots are written as `x ** 0.5`, and the tool description tells Claude to do this.
- **`string_operations`**: analyses a piece of text. It takes an `operation` parameter, which can be one of:
  - `word_count`
  - `char_count`
  - `most_common_word`
  - `longest_word`
  - `shortest_word`
  - `reading_time`

`string_operations` is one tool with a dispatcher that routes to six helper functions, so Claude sees one tool with an `operation` parameter instead of six separate tools.

## Example interactions

- "What is 347 \* 756?" -> calls `math_calculations`, answer: 262,332
- "How many words are in 'the quick brown fox jumps over the lazy dog'?" -> calls `string_operations` (`word_count`), answer: 9
- "How long will it take to read this paragraph?" -> calls `string_operations` (`reading_time`)
- "What is the capital of Morocco?" -> no tool, Claude answers directly

## Project structure

```
agent/
├── ui.py            # Streamlit chat interface and tool bubbles
├── agent.py         # Tool definitions, dispatcher, and the tool-calling loop
├── tools.py         # The local functions that actually run
├── requirements.txt
└── README.md
```

## Tech stack

- Python
- Anthropic Claude API (Haiku 4.5)
- Streamlit
- python-dotenv

## Run locally

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project folder:

```
ANTHROPIC_API_KEY=your_key_here
```

Then:

```bash
streamlit run ui.py
```

## Design decisions

- **`send_message` returns a dictionary** (`answer`, `tool_used`, `tool_input`, `tool_result`) instead of printing, so the UI can show the agent's steps and not just the final text.
- **Tools live in their own file** (`tools.py`) so the agent logic and the tool implementations stay separate.
- **The calculator is restricted.** It uses `eval()`, which can execute arbitrary Python, so the input is checked against an allowlist (digits, `+ - * / ( ) . %` and spaces) and built-ins are disabled. Without this, a public app could be prompted into running malicious code.
- **Unknown operations return a message**, not `None`, because passing `None` as a tool result makes the API call fail.

## Known limitations

These are real behaviours observed while testing, not hypotheticals.

- **No conversation memory.** Every message is handled independently. Asking "how many words does it have?" after pasting a text fails because Claude cannot see the earlier turn. Fixing this needs a persistent history, and tool turns add extra entries (the tool request and the tool result) that must be stored too.
- **One tool call per turn.** If Claude requests two tools in a single message, the code sends a result for only one of them and the API rejects the request.
- **Calculator is arithmetic only.** Functions like `sqrt()` return "Invalid expression" unless Claude rewrites them as `** 0.5`, which depends on the model following the tool description. Very large exponents (for example `9 ** 9 ** 9`) can hang the app.
- **String tools are naive.** Words are split on whitespace, so punctuation stays attached ("said." and "said" count as different words), and `most_common_word` is case-sensitive.
- **Reading time is returned in seconds** (assuming 200 words per minute), which is easy to misread for long texts.
- **Long inputs in tool bubbles.** The tool bubble prints the full input, so a long pasted article makes the chat very long.
- **No automated tests.** Behaviour was checked manually only.
- **Claude may not always use a tool.** For simple maths it can sometimes answer on its own; tool use is the model's decision, not guaranteed.

## Possible next steps

- Conversation memory that includes tool requests and results
- Handling several tool calls in one turn
- A safer expression parser instead of `eval()`
- Tests with a log of failure cases

## Author

Mohammed Aatif Minhaj
