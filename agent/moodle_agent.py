import asyncio
import base64
import json
import os
from pathlib import Path
from anthropic import Anthropic
from openai import AzureOpenAI, OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


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
        # Model can be overridden via MODEL environment variable
        self.model = os.environ.get("MODEL", "claude-sonnet-4.6")

        api_key = os.environ["ANTHROPIC_API_KEY"]
        base_url = os.environ["MOODLE_AI_BASE_URL"]

        # Auto-detect which client to use based on base URL
        if "moodle.com" in base_url or "anthropic.com" in base_url or base_url == "https://api.anthropic.com":
            # Anthropic API or Moodle AI Proxy (which is Anthropic-compatible)
            self.client = Anthropic(api_key=api_key, base_url=base_url)
            self.is_openai_compatible = False
        elif "azure" in base_url.lower() or "openai" in base_url.lower():
            # OpenAI-compatible endpoint (Azure, GitHub Copilot, etc.)
            # For Azure specifically, we need to use AzureOpenAI
            if "openai.azure.com" in base_url:
                self.client = AzureOpenAI(api_key=api_key, azure_endpoint=base_url)
            else:
                # Generic OpenAI-compatible endpoint
                self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.is_openai_compatible = True
        else:
            # Default to OpenAI-compatible if uncertain
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.is_openai_compatible = True

        self.moodle_url = os.environ["MOODLE_QA_URL"]
        self.run_dir = _next_run_dir()
        print(f"📁 Screenshots folder: {self.run_dir}")
        # Change to run directory so tools save files there by default
        self.original_cwd = os.getcwd()
        os.chdir(self.run_dir)

    def _save_screenshot(self, data: str, label: str = "screenshot") -> Path:
        """Save a base64-encoded screenshot into this run's folder."""
        try:
            # Ensure the run directory exists
            self.run_dir.mkdir(parents=True, exist_ok=True)

            # Use a counter so files sort in step order: 01_step.png, 02_evidence.png …
            existing = list(self.run_dir.glob("*.png"))
            index = len(existing) + 1
            path = self.run_dir / f"{index:02d}_{label}.png"

            # Decode and save the image
            image_bytes = base64.b64decode(data)
            path.write_bytes(image_bytes)
            print(f"   📸 Saved: {path}")
            return path
        except Exception as e:
            print(f"   ❌ Failed to save screenshot: {e}")
            raise

    def _move_orphaned_screenshots(self):
        """Move any PNG files that were saved to the original directory."""
        try:
            original_dir = Path(self.original_cwd)
            pngs = list(original_dir.glob("*.png"))
            if pngs:
                # Count existing files in run_dir to start numbering after them
                existing = list(self.run_dir.glob("*.png"))
                index = len(existing) + 1

                for png in pngs:
                    new_path = self.run_dir / f"{index:02d}_evidence.png"
                    png.rename(new_path)
                    print(f"   📸 Moved: {png.name} → {new_path}")
                    index += 1
        except Exception as e:
            print(f"   ⚠️  Could not move orphaned screenshots: {e}")


    async def run_test(self, test_steps: str):
        """Run a plain-English Moodle test using Chrome MCP."""

        # Set up environment for the MCP server
        server_env = os.environ.copy()
        server_env["SCREENSHOTS_DIR"] = str(self.run_dir)

        # Set Playwright/Chrome environment variables to suppress prompts
        # These are passed as environment variables to the Playwright process
        server_env["PLAYWRIGHT_LAUNCH_ARGS"] = " ".join([
            "--disable-password-manager-reauthentication",
            "--disable-prompt-on-repost",
            "--disable-session-crashed-bubble",
            "--disable-infobars",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
        ])

        server_params = StdioServerParameters(
            command="npx",
            # Run headed (not headless) — required for reliable drag-and-drop events.
            # Explicit viewport avoids Moodle's responsive breakpoints collapsing
            # the header into mobile layout (which is what happens at the default size).
            args=["@playwright/mcp", "--viewport-size", "1280,800"],
            env=server_env,
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
                    if self.is_openai_compatible:
                        # OpenAI API format: convert tools to OpenAI format
                        openai_tools = [
                            {
                                "type": "function",
                                "function": {
                                    "name": tool["name"],
                                    "description": tool["description"],
                                    "parameters": tool["input_schema"],
                                }
                            }
                            for tool in tools
                        ]

                        # Build messages with system prompt
                        openai_messages = [
                            {"role": "system", "content": system_prompt},
                        ] + messages

                        response = self.client.chat.completions.create(
                            model=self.model,
                            max_tokens=4096,
                            tools=openai_tools,
                            messages=openai_messages,
                        )

                        # Parse OpenAI response
                        stop_reason = response.choices[0].finish_reason
                        message = response.choices[0].message

                        # Print text content
                        if message.content:
                            print(f"\n🧠 {message.content}")

                        # Check if we're done
                        if stop_reason != "tool_calls":
                            print("\n" + "─" * 50)
                            print("🏁 Test run complete.")
                            break

                        # Extract tool calls from OpenAI response
                        tool_uses = message.tool_calls if hasattr(message, "tool_calls") and message.tool_calls else []
                        if not tool_uses:
                            break

                        # Convert to Anthropic-like format for processing
                        tool_uses_converted = []
                        for tool_call in tool_uses:
                            tool_uses_converted.append({
                                "id": tool_call.id,
                                "name": tool_call.function.name,
                                "input": json.loads(tool_call.function.arguments) if isinstance(tool_call.function.arguments, str) else tool_call.function.arguments,
                            })

                        # Add assistant turn with tool calls to history
                        messages.append({
                            "role": "assistant",
                            "content": message.content or "",
                            "tool_calls": tool_uses,  # Keep original for history
                        })

                    else:
                        # Anthropic API format
                        response = self.client.messages.create(
                            model=self.model,
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

                        tool_uses_converted = [
                            {
                                "id": tool_use.id,
                                "name": tool_use.name,
                                "input": tool_use.input,
                            }
                            for tool_use in tool_uses
                        ]

                        # Add assistant turn to history
                        messages.append({"role": "assistant", "content": response.content})

                    # Execute each tool via MCP
                    tool_results = []
                    for tool_use in tool_uses_converted:
                        print(f"\n🔧 {tool_use['name']}")
                        if tool_use['input']:
                            print(f"   args: {json.dumps(tool_use['input'])}")

                        try:
                            result = await session.call_tool(
                                tool_use['name'], arguments=tool_use['input']
                            )
                            # MCP tool results can be text or image content
                            content_parts = []
                            for item in result.content:
                                # Debug: print item type and attributes
                                item_type = type(item).__name__
                                print(f"   - Result item type: {item_type}")

                                if hasattr(item, "text"):
                                    text_content = item.text
                                    # Check if this is base64-encoded image data (starts with data:image)
                                    if text_content.startswith("data:image/"):
                                        # Extract base64 data from data URL
                                        try:
                                            b64_data = text_content.split(",", 1)[1]
                                            label = "evidence" if "screenshot" in tool_use['name'].lower() else "step"
                                            self._save_screenshot(b64_data, label)
                                            content_parts.append("[screenshot captured and saved]")
                                        except Exception as e:
                                            print(f"   ❌ Failed to parse base64 image data: {e}")
                                            content_parts.append(text_content)
                                    else:
                                        content_parts.append(text_content)
                                        preview = text_content[:300]
                                        print(f"   ↳ {preview}{'...' if len(text_content) > 300 else ''}")
                                elif hasattr(item, "data"):
                                    # Direct base64 data in MCP response
                                    label = "evidence" if "screenshot" in tool_use.name.lower() else "step"
                                    self._save_screenshot(item.data, label)
                                    content_parts.append("[screenshot captured and saved]")
                                elif hasattr(item, "mimeType") and "image" in item.mimeType:
                                    # Image content type
                                    if hasattr(item, "base64"):
                                        label = "evidence" if "screenshot" in tool_use.name.lower() else "step"
                                        self._save_screenshot(item.base64, label)
                                        content_parts.append("[screenshot captured and saved]")
                                else:
                                    # Debug: show all attributes if it doesn't match expected types
                                    print(f"   - Attributes: {[a for a in dir(item) if not a.startswith('_')]}")
                            content = "\n".join(content_parts) if content_parts else "OK"
                        except Exception as e:
                            content = f"ERROR: {str(e)}"
                            print(f"   ↳ ❌ {content}")

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use['id'],
                            "content": content,
                        })

                    # Feed results back to the model
                    if self.is_openai_compatible:
                        # OpenAI format: tool results go as separate messages with role="tool"
                        for tr in tool_results:
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tr["tool_use_id"],
                                "content": tr["content"],
                            })
                    else:
                        # Anthropic format
                        messages.append({"role": "user", "content": tool_results})

        # Cleanup: move any orphaned screenshots from original directory
        self._move_orphaned_screenshots()
        # Restore original working directory
        os.chdir(self.original_cwd)
