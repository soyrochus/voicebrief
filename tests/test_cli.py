import sys
import types
from pathlib import Path

import pytest

import voicebrief.__main__ as cli


def test_gui_flag_is_exclusive():
    with pytest.raises(SystemExit) as exc:
        cli.main(["--gui", "example.mp3"])
    assert exc.value.code == 2


def test_gui_flag_launches_gui(monkeypatch):
    invoked = False

    def fake_launch() -> None:
        nonlocal invoked
        invoked = True

    module = types.SimpleNamespace(launch_gui=fake_launch)
    monkeypatch.setitem(sys.modules, "voicebrief.gui", module)

    cli.main(["--gui"])
    assert invoked


def test_prompt_file_is_forwarded_to_run_voicebrief(monkeypatch, tmp_path: Path):
    prompt_file = tmp_path / "instructions.txt"
    prompt_file.write_text("Preserve speaker names.", encoding="utf-8")
    captured: dict[str, object] = {}

    def fake_run_voicebrief(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs

        class Result:
            optimized_transcript = None
            markdown_transcript = None
            source_path = Path("example.mp3")

        return Result()

    monkeypatch.setattr(cli, "run_voicebrief", fake_run_voicebrief)

    cli.main(["example.mp3", "--prompt-file", str(prompt_file)])

    assert captured["kwargs"]["custom_instructions"] == "Preserve speaker names."


def test_custom_instructions_and_prompt_file_cannot_be_combined():
    with pytest.raises(SystemExit) as exc:
        cli.main(
            [
                "example.mp3",
                "--custom-instructions",
                "Keep headings short.",
                "--prompt-file",
                "instructions.txt",
            ]
        )

    assert exc.value.code == 1
