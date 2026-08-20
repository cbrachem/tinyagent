import json
import subprocess

from openai import OpenAI


def bash_call(command):
    r = subprocess.run(command, shell=True, capture_output=True)
    return r.stdout.decode()


SYSTEM_PROMPT = """
You are an expert coding assistant operating inside a coding agent harness.
You help users by reading files, executing commands, editing code, and writing new files.
Prefer creating code as a file in the current directory over including it in the answer.
"""

TOOLS = [
    {
        "type": "function",
        "name": "bash",
        "description": "Run a shell command in the current working directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to run.",
                }
            },
            "required": ["command"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]

client = OpenAI()
conversation = []

RED = "\033[0;31m"
YELLOW = "\033[0;33m"
NC = "\033[0m"

while True:
    message = input(f"{YELLOW}You:{NC} ")
    if not message:
        break
    conversation.append({"role": "user", "content": message})

    while True:
        response = client.responses.create(
            model="gpt-5.6-luna",
            instructions=SYSTEM_PROMPT,
            input=conversation,
            tools=TOOLS,
        )
        conversation.extend(response.output)
        tool_calls = [item for item in response.output if item.type == "function_call"]

        if not tool_calls:
            print(f"{RED}Luna:{NC} {response.output_text}")
            break

        for tool_call in tool_calls:
            if tool_call.name != "bash":
                output = f"Unknown tool: {tool_call.name}"
            else:
                try:
                    arguments = json.loads(tool_call.arguments)
                    command = arguments["command"]
                    print(f"tool call: {command.splitlines()[0]}...")
                    output = bash_call(command)
                except Exception as e:
                    output = f"Error: {e}"

            conversation.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": output,
                }
            )
