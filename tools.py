"""Local tools for the agent.

Claude never runs these by itself. It only "requests" a tool by name with inputs, my code runs the matching function here and sends the result back.
"""
import re
from collections import Counter


def calculate(exp):
    """
    This evaluates a math expression such as '347 * 756' or '121 ** 0.5'.
    # eval() runs arbitrary Python, so only allow digits, operators and brackets.
    # Without this check, a user could prompt Claude into running malicious code.
    """

    if not re.fullmatch(r"[0-9+\-*/().%\s]+", exp):
        return "Invalid expression."
    try:
        return str(eval(exp, {"__builtins__": {}}, {}))
    except Exception:
        return "Invalid expression."


def word_count(exp):
    # Number of words (split on whitespace).
    return str(len(exp.split()))


def char_count(exp):
    # Number of characters, including spaces.
    return str(len(exp))


def longest_word(exp):
    # Longest word by length.
    return max(exp.split(), key=len)


def shortest_word(exp):
    # Shortest word by length.
    return min(exp.split(), key=len)


def most_common_word(exp):
    # Most frequent word (case-sensitive).
    return Counter(exp.split()).most_common(1)[0][0]


def reading_time(exp):
    # Estimated reading time in SECONDS, assuming 200 words per minute.
    wpm = 200
    return str(round(len(exp.split()) / wpm * 60, 1))
