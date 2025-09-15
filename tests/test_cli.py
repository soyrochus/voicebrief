import sys
import types

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
