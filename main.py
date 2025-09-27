import os
import sys
import shutil
import textwrap

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
  if not os.getenv("ZAPIER_MCP_API_KEY"):
    print("Error: ZAPIER_MCP_API_KEY is not set. Export it before running.")
    print("Example: export ZAPIER_MCP_API_KEY=...")
    sys.exit(1)


def _print_help() -> None:
  print("CLI AI Agent (Responses API + Zapier MCP)\n")
  print("Commands: /exit, /help, /clear, /powers, /examples\n")


def _terminal_width() -> int:
  try:
    return max(40, shutil.get_terminal_size(fallback=(100, 24)).columns)
  except Exception:
    return 100


def _wrap(text: str, width: int) -> str:
  return "\n".join(textwrap.fill(line, width=width) if line.strip() else "" for line in text.splitlines())


def _init_colors():
  try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init()
    return True, Fore, Style
  except Exception:
    class _Dummy:
      RESET_ALL = ""
      BRIGHT = ""
      DIM = ""
      GREEN = ""
      CYAN = ""
      MAGENTA = ""
      YELLOW = ""
      RED = ""
      WHITE = ""
      BLUE = ""
    return False, _Dummy(), _Dummy()


def _print_powers(width: int, Fore, Style) -> None:
  lines = [
    "What I can do via Zapier MCP:",
    "- Google Docs: create, update, share documents",
    "- Google Sheets: create sheets, update cells, run lookups",
    "- Google Calendar: find/add/update events, busy times",
    "- Google Meet: schedule meetings and share links",
    "- Google Drive: search/upload/manage files",
    "- Google Forms: create forms",
    "- Gmail: draft/reply/send, label, find emails",
    "- Telegram: send messages/photos/polls",
    "- WhatsApp: send messages (where available)",
  ]
  print((Style.BRIGHT if hasattr(Style, 'BRIGHT') else "") + _wrap("\n".join(lines), width) + (Style.RESET_ALL if hasattr(Style, 'RESET_ALL') else ""))


def _print_examples(width: int, Fore, Style) -> None:
  examples = [
    "Schedule a meeting: 'Schedule a Google Meet on 20 Oct 2025, 10:00-11:00 with John Doe. My email abdibrokhim@gmail.com, his email theelofiguy@gmail.com. Send him a casual invite email.'",
    "Email: 'Draft an email in Gmail to jane@acme.com about our roadmap, cc team@acme.com'",
    "Sheets: 'Create a budget sheet with columns: Item, Cost, Owner'",
    "Docs: 'Create a project brief titled Project Zap with key sections'",
    "Drive: 'Find the file Quarterly Report.pdf and share with ops@acme.com'",
    "Telegram: 'Send a message to @mychannel: Team standup in 10 minutes'",
  ]
  header = (Style.BRIGHT if hasattr(Style, 'BRIGHT') else "") + "Try these:" + (Style.RESET_ALL if hasattr(Style, 'RESET_ALL') else "")
  print(header)
  for ex in examples:
    print("  - " + _wrap(ex, width - 4))


def _run_responses_cli(user_display_name: str) -> None:
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

  has_color, Fore, Style = _init_colors()
  width = _terminal_width()
  print((Style.DIM if hasattr(Style, 'DIM') else "") + _wrap("Connected: OpenAI Responses API + Zapier MCP (tool choice: required)", width) + (Style.RESET_ALL if hasattr(Style, 'RESET_ALL') else ""))
  print(_wrap("Type /powers or /examples to get started.", width))
  while True:
    try:
      prompt_label = f"{user_display_name}: "
      user_input = input(prompt_label)
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
    if text == "/powers":
      _print_powers(width, Fore, Style)
      continue
    if text == "/examples":
      _print_examples(width, Fore, Style)
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
      role_label = (Fore.GREEN if hasattr(Fore, 'GREEN') else "") + "Assistant" + (Style.RESET_ALL if hasattr(Style, 'RESET_ALL') else "")
      print(f"{role_label}:\n" + _wrap(output, width))
    except Exception as e:
      err_label = (Fore.RED if hasattr(Fore, 'RED') else "") + "Error" + (Style.RESET_ALL if hasattr(Style, 'RESET_ALL') else "")
      print(f"{err_label}: {e}")


def main() -> None:
  _ensure_api_key()

  # ASCII banner using 'art' library (if available)
  try:
    from art import tprint
    tprint("CLI Agent", "rnd-xlarge")
  except Exception:
    print("CLI Agent")

  # Interactive intro: collect display name and show quick tips
  has_color, Fore, Style = _init_colors()
  width = _terminal_width()
  display_name = "You"
  try:
    name_input = input("Your name (optional): ").strip()
    if name_input:
      display_name = name_input
  except Exception:
    pass
  tips = [
    "Tips:",
    "- Use natural language; I will pick the right Zapier tool",
    "- Use /powers to see available integrations",
    "- Use /examples for sample prompts",
    "- Use /clear to clean the screen",
  ]
  print(_wrap("\n".join(tips), width))

  _run_responses_cli(display_name)


if __name__ == "__main__":
  main()
