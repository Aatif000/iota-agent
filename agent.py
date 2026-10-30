"""
Agent logic: sends the user's message to Agent with tools attached,
runs any tool Claude requests and returns the result for the UI.
"""

import anthropic
import os
from dotenv import load_dotenv
from tools import *

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Tools are defined below so the Agent reads and decides how and when to use a tool.
tools = [
    {
        "name": "math_calculations",
        "description": "Evaluates a math expression and returns the result",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The math expression to evaluate e.g. '347 * 756'. For square roots use e.g. '121 ** 0.5'."
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "string_operations",
        "description": "Analyses a piece of text: word count, character count, most common word, longest word, shortest word, or reading time",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The text to analyse"
                },
                "operation": {
                    "type": "string",
                    "description": "One of: word_count, char_count, most_common_word, longest_word, shortest_word, reading_time"
                }
            },
            "required": ["expression", "operation"]
        }
    }
]


def string_operations(exp, operation):
    # Dispatcher: routes one 'string_operations' tool call to the right helper.
    if operation == "word_count":
        return word_count(exp)
    elif operation == "char_count":
        return char_count(exp)
    elif operation == "longest_word":
        return longest_word(exp)
    elif operation == "shortest_word":
        return shortest_word(exp)
    elif operation == "reading_time":
        return reading_time(exp)
    elif operation == "most_common_word":
        return most_common_word(exp)
    # Fallback: returning None here would crash the API call later
    return "Unknown operation."


def send_message(user_message):
    """Run one agent turn.

    Flow: send message + tools -> Agent may request a tool -> we run it locally -> send the result back -> Agent writes the final answer.

    Returns a dict the UI can display:
    answer, tool_used, tool_input, tool_result (tool fields are None if no tool ran).
    """
    result = {
        "answer": None,
        "tool_used": None,
        "tool_input": None,
        "tool_result": None
    }

    # Send the user's message together with the available tools
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        tools=tools,
        messages=[{"role": "user", "content": user_message}]
    )

    # stop_reason = "tool_use" means Agent is asking us to run a tool
    if response.stop_reason == "tool_use":
        for block in response.content:
            if block.type == "tool_use":

                # Run the requested tool locally
                if block.name == "math_calculations":
                    expression = block.input["expression"]
                    result["tool_input"] = expression
                    result["tool_used"] = block.name
                    result["tool_result"] = calculate(expression)

                if block.name == "string_operations":
                    expression = block.input["expression"]
                    result["tool_input"] = expression
                    result["tool_used"] = block.name
                    result["tool_result"] = string_operations(
                        expression, block.input["operation"])

                # Send the tool result back so Agent can write the final answer.
                # Agent needs the full chain: question -> its tool request -> our result.
                second_response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    tools=tools,
                    messages=[
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": response.content},
                        {"role": "user",
                         "content": [
                             {"type": "tool_result",
                              "tool_use_id": block.id,  # links the result to Agent's request
                              "content": result["tool_result"]}]}
                    ]
                )
                result["answer"] = second_response.content[0].text
    else:
        # If no tool is needed then Agent answers directly
        result["answer"] = response.content[0].text

    return result
