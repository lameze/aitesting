import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
from agent.moodle_agent import MoodleAgent

load_dotenv()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python runner.py tests/<test_file>.md")
        print("\nAvailable tests:")
        for f in sorted(Path("tests").glob("*.md")):
            print(f"  {f}")
        sys.exit(1)

    test_file = Path(sys.argv[1])
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        sys.exit(1)

    test_steps = test_file.read_text()

    print(f"\n📋 Test file : {test_file.name}")
    print(f"{'═' * 50}")
    print(test_steps.strip())
    print(f"{'═' * 50}\n")

    agent = MoodleAgent()
    await agent.run_test(test_steps)


if __name__ == "__main__":
    asyncio.run(main())

