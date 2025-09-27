import os
import sys

try:
  from dotenv import load_dotenv
  load_dotenv()
except Exception:
  pass


def _ensure_api_key() -> None:
  if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY is not set. Export it before running.")
    print("Example: export OPENAI_API_KEY=sk-...")
    sys.exit(1)


def _print_help() -> None:
  print("CLI AI Agent (Responses API + Zapier MCP)\n")
  print("Commands: /exit to quit, /help to show this, /clear to reset screen\n")


def _run_responses_cli() -> None:
  from openai import OpenAI

  client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
  zapier_mcp_api_key = os.getenv("ZAPIER_MCP_API_KEY")

  tools = [
    {
      "type": "mcp",
      "server_label": "zapier",
      "server_url": "https://mcp.zapier.com/api/mcp/mcp",
      "require_approval": "never",
      "headers": {
        "Authorization": f"Bearer {zapier_mcp_api_key}"
      }
    }
  ]

  print("Assistant ready (Responses API). Type your message. /exit to quit, /help for help.")
  while True:
    try:
      user_input = input("You: ")
    except (EOFError, KeyboardInterrupt):
      print("\nExiting.")
      break

    text = user_input.strip()
    if not text:
      continue
    if text in ("/exit", "/quit"):
      print("Goodbye!")
      break
    if text == "/help":
      _print_help()
      continue
    if text == "/clear":
      try:
        os.system("clear" if os.name != "nt" else "cls")
      except Exception:
        pass
      continue

    try:
      resp = client.responses.create(
        model="gpt-5-mini",
        input=text,
        tools=tools,
        tool_choice="required",
      )
      output = None
      try:
        output = resp.output_text
      except Exception:
        pass
      if not output:
        try:
          out_parts = []
          for item in getattr(resp, "output", []) or []:
            if getattr(item, "type", "") == "output_text":
              out_parts.append(getattr(item, "text", ""))
          output = "".join(out_parts) if out_parts else None
        except Exception:
          output = None
      if not output:
        output = "(no text output)"
      print(f"Assistant: {output}")
    except Exception as e:
      print(f"Error: {e}")


def main() -> None:
  _ensure_api_key()

  # ASCII banner using 'art' library (if available)
  try:
    from art import tprint
    tprint("CLI Agent", "rnd-xlarge")
  except Exception:
    print("CLI Agent")

  _run_responses_cli()


if __name__ == "__main__":
  main()