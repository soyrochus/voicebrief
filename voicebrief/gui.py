"""GTK-based graphical interface for Voicebrief."""
from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from voicebrief.app import run_voicebrief
from voicebrief.logging_utils import configure_logging


@dataclass(slots=True)
class _GuiConfig:
    source: Optional[Path] = None
    destination: Optional[Path] = None
    force_video: bool = False
    auto_detect: bool = True
    log_level: str = "INFO"


def launch_gui() -> None:
    """Launch the GTK GUI.

    Raises
    ------
    RuntimeError
        If the GTK bindings are not available on the current system.
    """

    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Gdk", "4.0")
        from gi.repository import Gdk, Gio, GLib, Gtk
    except (ImportError, ValueError) as exc:  # pragma: no cover - environment specific
        raise RuntimeError(
            "GTK 4 runtime is required to use the Voicebrief GUI. "
            "Install PyGObject and ensure a GTK runtime is available."
        ) from exc

    _init_result = Gtk.init_check()
    success = _init_result[0] if isinstance(_init_result, tuple) else bool(_init_result)
    if not success:  # pragma: no cover - environment specific
        raise RuntimeError(
            "Unable to initialise GTK. Ensure a graphical session is available."
        )

    if Gdk.Display.get_default() is None:  # pragma: no cover - environment specific
        raise RuntimeError(
            "No graphical display detected. Launch Voicebrief from a graphical session."
        )

    configure_logging("INFO")

    class GtkTextViewHandler(logging.Handler):
        def __init__(self, buffer: Gtk.TextBuffer):
            super().__init__()
            self._buffer = buffer
            self.setFormatter(
                logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
            )

        def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - UI thread
            message = self.format(record)
            GLib.idle_add(self._append_message, message + "\n")

        def _append_message(self, message: str) -> None:
            self._buffer.insert(self._buffer.get_end_iter(), message)

    class VoicebriefWindow(Gtk.ApplicationWindow):  # pragma: no cover - UI
        def __init__(self, app: Gtk.Application):
            super().__init__(application=app, title="Voicebrief")
            self.set_default_size(720, 500)
            self.set_margin_start(24)
            self.set_margin_end(24)
            self.set_margin_top(24)
            self.set_margin_bottom(24)

            self._config = _GuiConfig()

            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            self.set_child(main_box)

            # Source selector
            self._source_entry = Gtk.Entry(placeholder_text="Select an audio or video file...")
            self._source_entry.set_editable(False)
            source_button = Gtk.Button(label="Browse...")
            source_button.connect("clicked", self._choose_source)

            source_box = Gtk.Box(spacing=6)
            source_box.append(self._source_entry)
            source_box.append(source_button)
            main_box.append(source_box)

            # Destination selector
            self._destination_entry = Gtk.Entry(placeholder_text="Optional destination directory...")
            self._destination_entry.set_editable(False)
            dest_button = Gtk.Button(label="Choose...")
            dest_button.connect("clicked", self._choose_destination)

            dest_box = Gtk.Box(spacing=6)
            dest_box.append(self._destination_entry)
            dest_box.append(dest_button)
            main_box.append(dest_box)

            # Options row
            options_box = Gtk.Box(spacing=24)

            self._force_video_switch = Gtk.Switch()
            self._force_video_switch.set_valign(Gtk.Align.CENTER)
            force_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            force_box.append(Gtk.Label(label="Force video extraction", xalign=0))
            force_box.append(self._force_video_switch)
            options_box.append(force_box)

            self._auto_detect_switch = Gtk.Switch()
            self._auto_detect_switch.set_valign(Gtk.Align.CENTER)
            self._auto_detect_switch.set_active(True)
            auto_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            auto_box.append(Gtk.Label(label="Auto-detect video by extension", xalign=0))
            auto_box.append(self._auto_detect_switch)
            options_box.append(auto_box)

            # Log level combo
            levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
            self._log_combo = Gtk.DropDown.new_from_strings(levels)
            self._log_combo.set_selected(levels.index("INFO"))
            log_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            log_box.append(Gtk.Label(label="Log level", xalign=0))
            log_box.append(self._log_combo)
            options_box.append(log_box)

            main_box.append(options_box)

            # Run button
            self._run_button = Gtk.Button(label="Start Processing")
            self._run_button.add_css_class("suggested-action")
            self._run_button.connect("clicked", self._start_processing)
            main_box.append(self._run_button)

            # Output log view
            log_frame = Gtk.Frame(label="Activity log")
            scrolled = Gtk.ScrolledWindow()
            self._log_buffer = Gtk.TextBuffer()
            log_view = Gtk.TextView(buffer=self._log_buffer)
            log_view.set_editable(False)
            log_view.set_monospace(True)
            scrolled.set_child(log_view)
            log_frame.set_child(scrolled)
            main_box.append(log_frame)

            self._log_handler = GtkTextViewHandler(self._log_buffer)
            logging.getLogger().addHandler(self._log_handler)
            logging.getLogger().setLevel(logging.INFO)
            self.connect("destroy", self._on_destroy)

        def _choose_source(self, _button: Gtk.Button) -> None:
            dialog = Gtk.FileDialog()

            def _on_open(dialog_ref: Gtk.FileDialog, result: Gio.AsyncResult) -> None:
                try:
                    file = dialog_ref.open_finish(result)
                except GLib.Error as err:  # pragma: no cover - UI thread
                    if err.domain == Gtk.DialogError.quark():
                        return
                    self._show_error(err.message)
                    return

                if file is None:
                    return

                filename = file.get_path()
                if filename:
                    self._source_entry.set_text(filename)
                    self._config.source = Path(filename)

            dialog.set_title("Select audio or video file")
            dialog.open(self, None, _on_open)

        def _choose_destination(self, _button: Gtk.Button) -> None:
            dialog = Gtk.FileDialog()

            def _on_select(dialog_ref: Gtk.FileDialog, result: Gio.AsyncResult) -> None:
                try:
                    folder = dialog_ref.select_folder_finish(result)
                except GLib.Error as err:  # pragma: no cover - UI thread
                    if err.domain == Gtk.DialogError.quark():
                        return
                    self._show_error(err.message)
                    return

                if folder is None:
                    return

                filename = folder.get_path()
                if filename:
                    self._destination_entry.set_text(filename)
                    self._config.destination = Path(filename)

            dialog.set_title("Select destination directory")
            dialog.select_folder(self, None, _on_select)

        def _start_processing(self, _button: Gtk.Button) -> None:
            if not self._config.source and not self._source_entry.get_text():
                self._show_error("Select a source file before starting.")
                return

            source_path = Path(self._source_entry.get_text())
            if not source_path.exists():
                self._show_error("Selected source file does not exist.")
                return

            self._config.source = source_path
            if self._destination_entry.get_text():
                self._config.destination = Path(self._destination_entry.get_text())
            else:
                self._config.destination = None

            self._config.force_video = self._force_video_switch.get_active()
            self._config.auto_detect = self._auto_detect_switch.get_active()
            selected_item = self._log_combo.get_selected_item()
            log_level = (
                selected_item.get_string() if selected_item is not None else "INFO"
            )
            self._config.log_level = log_level

            logging.getLogger().setLevel(getattr(logging, log_level, logging.INFO))

            self._run_button.set_sensitive(False)
            self._append_status("Starting processing...\n")

            def worker() -> None:
                try:
                    result = run_voicebrief(
                        self._config.source,
                        destination=self._config.destination,
                        force_video=self._config.force_video,
                        auto_detect_video=self._config.auto_detect,
                    )
                except Exception as exc:  # pragma: no cover - UI thread
                    logging.getLogger("voicebrief.gui").exception("Processing failed")
                    GLib.idle_add(self._show_error, str(exc))
                else:  # pragma: no cover - UI thread
                    details = (
                        f"Finished. Optimized transcript stored at: {result.optimized_transcript.text_path}\n"
                    )
                    GLib.idle_add(self._append_status, details)
                finally:  # pragma: no cover - UI thread
                    GLib.idle_add(self._run_button.set_sensitive, True)

            threading.Thread(target=worker, daemon=True).start()

        def _append_status(self, message: str) -> None:
            self._log_buffer.insert(self._log_buffer.get_end_iter(), message)

        def _show_error(self, message: str) -> None:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=message,
            )
            dialog.connect("response", lambda d, *_: d.destroy())
            dialog.present()

        def _on_destroy(self, *_args) -> None:
            logging.getLogger().removeHandler(self._log_handler)

    class VoicebriefApplication(Gtk.Application):  # pragma: no cover - UI
        def __init__(self):
            super().__init__(application_id="dev.voicebrief.app")

        def do_activate(self, *args):
            window = VoicebriefWindow(self)
            window.present()

    app = VoicebriefApplication()
    try:
        app.run([])
    except RuntimeError as exc:  # pragma: no cover - environment specific
        raise RuntimeError(
            "Failed to start the GTK interface. Ensure a graphical session is available."
        ) from exc
