import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = sorted((ROOT / "agents").glob("*.md"))

# claude code tool names an agent may list; anything else is a typo that
# silently drops the tool
KNOWN_TOOLS = {
    "Agent",
    "AskUserQuestion",
    "Bash",
    "Edit",
    "Glob",
    "Grep",
    "LSP",
    "NotebookEdit",
    "Read",
    "SendMessage",
    "SendUserFile",
    "Skill",
    "TaskStop",
    "ToolSearch",
    "WebFetch",
    "WebSearch",
    "Write",
}
WRITE_TOOLS = {"Edit", "Write", "NotebookEdit"}
READ_ONLY = {
    "auth-reviewer",
    "code-reviewer",
    "go-k8s-reviewer",
    "refine",
    "release-notes",
    "router",
    "security-auditor",
    "test-verifier",
    "triage",
    "verifier",
}


def frontmatter(path: Path) -> dict[str, str]:
    match = re.match(r"---\n(.*?)\n---\n", path.read_text(), re.S)
    if not match:
        return {}
    fields = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and not line[:1].isspace():
            fields[key.strip()] = value.strip()
    return fields


def tools(path: Path) -> set[str]:
    raw = frontmatter(path).get("tools", "")
    return {entry.strip() for entry in raw.split(",") if entry.strip()}


class AgentToolsTest(unittest.TestCase):
    def test_agents_exist(self) -> None:
        self.assertTrue(AGENTS)

    def test_every_agent_declares_a_tool_allowlist(self) -> None:
        # without one an agent inherits every built-in and every mcp schema
        for path in AGENTS:
            with self.subTest(agent=path.stem):
                self.assertTrue(tools(path), f"{path.name} has no tools: allowlist")

    def test_tool_names_are_known_or_mcp_patterns(self) -> None:
        for path in AGENTS:
            for tool in tools(path):
                with self.subTest(agent=path.stem, tool=tool):
                    if tool.startswith("mcp__"):
                        self.assertNotIn("*", tool, "name a server, not every mcp tool")
                    else:
                        self.assertIn(tool, KNOWN_TOOLS)

    def test_only_the_router_dispatches_agents(self) -> None:
        for path in AGENTS:
            with self.subTest(agent=path.stem):
                if path.stem == "router":
                    self.assertIn("Agent", tools(path))
                else:
                    self.assertNotIn("Agent", tools(path))

    def test_read_only_agents_cannot_edit_files(self) -> None:
        for path in AGENTS:
            if path.stem in READ_ONLY:
                with self.subTest(agent=path.stem):
                    self.assertFalse(tools(path) & WRITE_TOOLS)


if __name__ == "__main__":
    unittest.main()
