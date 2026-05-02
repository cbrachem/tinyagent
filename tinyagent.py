import subprocess
import inspect
from openai import OpenAI
import json


def bash_call(command):
    r = subprocess.run(command, shell=True, capture_output=True)
    return r.stdout.decode()


SYSTEM_PROMPT = """
You are an expert coding assistant operating inside a coding agent harness.
You help users by reading files, executing commands, editing code, and writing new files.
Prefer creating code as a file in teh current directory over including it in the answer.

You have two valid response modes:

1. Normal response mode:
   - Answer the user directly in plain text.

2. Tool call mode:
   - If you need a shell command, respond with exactly:
     tool:bash:COMMAND
   - The entire message must contain only that single tool call.
   - No markdown, no commentary, no extra whitespace before or after.

After a tool result is provided, continue from that result in normal response mode.
"""

client = OpenAI()
conversation = [
    {"role": "developer", "content": SYSTEM_PROMPT},
]

RED = "\033[0;31m"
YELLOW = "\033[0;33m"
NC = "\033[0m"

tool_call = None

while True:
    if tool_call:
        output = bash_call(tool_call)
        # print("Tool output")
        # print("-" * 10)
        # print(output)
        message = f"tool_result:{output}"
        tool_call = None
    else:
        message = input(f"{YELLOW}You:{NC} ")
        if not message:
            break
    conversation.append({"role": "user", "content": message})

    completion = client.chat.completions.create(
        model="gpt-5.4-mini", messages=conversation
    )
    answer = completion.choices[0].message
    conversation.append(answer)

    if answer.content.lstrip().startswith("tool:bash:"):
        try:
            tool_call = answer.content.split(":", maxsplit=2)[2]
            print(f"tool call: {tool_call.splitlines()[0]}...")
        except Exception as e:
            print(f"Error: {e}")
            print(answer.content)
    else:
        print(f"{RED}GPT:{NC} {answer.content}")
