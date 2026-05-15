import asyncio
import base64
import json
import os
from pathlib import Path
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MODEL = "claude-sonnet-4.6"

# Always resolve screenshots relative to the project root (where this package lives)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS_BASE = PROJECT_ROOT / "screenshots"


def _next_run_dir() -> Path:
    """Return the next numbered run folder, e.g. screenshots/3/"""
    SCREENSHOTS_BASE.mkdir(exist_ok=True)
    existing = sorted(
        [int(p.name) for p in SCREENSHOTS_BASE.iterdir() if p.is_dir() and p.name.isdigit()],
    )
    next_num = (existing[-1] + 1) if existing else 1
    run_dir = SCREENSHOTS_BASE / str(next_num)
    run_dir.mkdir()
    return run_dir


class MoodleAgent:
    def __init__(self):
        self.client = Anthropic(
            api_key=os.environ["ANTHROPIC_API_KEY"],
            base_url=os.environ["MOODLE_AI_BASE_URL"],
        )
        self.moodle_url = os.environ["MOODLE_QA_URL"]
        self.run_dir = _next_run_dir()
        print(f"📁 Screenshots folder: {self.run_dir}")

    def _save_screenshot(self, data: str, label: str = "screenshot") -> Path:
        """Save a base64-encoded screenshot into this run's folder."""
        # Use a counter so files sort in step order: 01_step.png, 02_evidence.png …
        existing = list(self.run_dir.glob("*.png"))
        index = len(existing) + 1
        path = self.run_dir / f"{index:02d}_{label}.png"
        path.write_bytes(base64.b64decode(data))
        print(f"   📸 Saved: {path}")
        return path

    async def run_test(self, test_steps: str):
        """Run a plain-English Moodle test using Chrome MCP."""

        server_params = StdioServerParameters(
            command="npx",
            # Run headed (not headless) — required for reliable drag-and-drop events.
            # Explicit viewport avoids Moodle's responsive breakpoints collapsing
            # the header into mobile layout (which is what happens at the default size).
            args=["@playwright/mcp", "--viewport-size", "1280,800"],
            env=None,
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools_result = await session.list_tools()
                tools = [
                    {
                        "name": t.name,
                        "description": t.description,
                        "input_schema": t.inputSchema,
                    }
                    for t in tools_result.tools
                ]

                print(f"✅ Chrome MCP connected — {len(tools)} browser tools available\n")

                system_prompt = f"""You are a Moodle QA test automation agent.
You have access to a real browser via tools. The Moodle site under test is: {self.moodle_url}

Your job:
1. Read the test steps provided by the user
2. Execute each step precisely using the browser tools
3. After each step, confirm the expected state using a snapshot or screenshot
4. Report PASS ✅ or FAIL ❌ with details for each step
5. At the end, print a summary of the full test result

Rules:
- Do not guess at element locations — always take a snapshot to confirm page state first
- If an assertion fails, report FAIL immediately and stop
- Be concise in your output, focus on results not narration

Moodle edit mode guidance:
- The edit mode toggle is a CHECKBOX (input[name="setmode"]) inside a form that submits to /editmode.php
- To enable edit mode: click the checkbox input — do NOT just click the label text
- After clicking, the page will reload — wait for it to finish, then verify editing controls are visible
  (e.g. "Add an activity or resource" links appear in each section)
- If the snapshot shows the checkbox is already checked, edit mode is already ON — do not click it again

Drag and drop guidance:
- Moodle course page drag-and-drop uses a move icon (≡ or ⠿) next to each activity
- To drag an activity: use the drag_and_drop tool targeting the move handle of the activity
- Always take a snapshot AFTER the drop to verify the new position
- If the drag tool is unavailable, try using browser_drag_and_drop with precise element selectors
- After a successful drop, take a screenshot as evidence"""

                messages = [
                    {
                        "role": "user",
                        "content": f"Please execute the following Moodle test:\n\n{test_steps}",
                    }
                ]

                print("🤖 Agent starting...\n" + "─" * 50)

                # Agentic loop
                while True:
                    response = self.client.messages.create(
                        model=MODEL,
                        max_tokens=4096,
                        system=system_prompt,
                        tools=tools,
                        messages=messages,
                    )

                    # Print any text output from the model
                    for block in response.content:
                        if hasattr(block, "text") and block.text:
                            print(f"\n🧠 {block.text}")

                    # Done — no more tool calls
                    if response.stop_reason == "end_turn":
                        print("\n" + "─" * 50)
                        print("🏁 Test run complete.")
                        break

                    # Collect tool calls
                    tool_uses = [b for b in response.content if b.type == "tool_use"]
                    if not tool_uses:
                        break

                    # Add assistant turn to history
                    messages.append({"role": "assistant", "content": response.content})

                    # Execute each tool via MCP
                    tool_results = []
                    for tool_use in tool_uses:
                        print(f"\n🔧 {tool_use.name}")
                        if tool_use.input:
                            print(f"   args: {json.dumps(tool_use.input)}")

                        try:
                            result = await session.call_tool(
                                tool_use.name, arguments=tool_use.input
                            )
                            # MCP tool results can be text or image content
                            content_parts = []
                            for item in result.content:
                                if hasattr(item, "text"):
                                    content_parts.append(item.text)
                                    preview = item.text[:300]
                                    print(f"   ↳ {preview}{'...' if len(item.text) > 300 else ''}")
                                elif hasattr(item, "data"):
                                    # Save screenshot to disk
                                    label = "evidence" if "screenshot" in tool_use.name.lower() else "step"
                                    self._save_screenshot(item.data, label)
                                    content_parts.append("[screenshot captured and saved]")
                            content = "\n".join(content_parts) if content_parts else "OK"
                        except Exception as e:
                            content = f"ERROR: {str(e)}"
                            print(f"   ↳ ❌ {content}")

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": content,
                        })

                    # Feed results back to the model
                    messages.append({"role": "user", "content": tool_results})

