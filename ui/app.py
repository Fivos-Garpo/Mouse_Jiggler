"""Modern Tkinter user interface for Mouse Jiggler."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from core.jiggler import JigglerConfig, MouseJiggler


class MouseJigglerApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Mouse Jiggler")
        self.root.geometry("440x540")
        self.root.minsize(420, 520)
        self.root.resizable(False, False)

        self._style = ttk.Style(self.root)
        try:
            self._style.theme_use("vista")
        except tk.TclError:
            pass

        self._style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        self._style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        self._style.configure("Card.TLabelframe", padding=16)
        self._style.configure("Status.TLabel", font=("Segoe UI", 10, "bold"))
        self._style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 8),
        )

        self.max_delay = tk.StringVar(value="10")
        self.duration = tk.StringVar(value="60")
        self.status = tk.StringVar(value="Ready")
        self.time_left = tk.StringVar(value="00:00:00")

        self.jiggler = MouseJiggler(on_status=self._on_status)
        self._build_ui()
        self._refresh()
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=24)
        outer.pack(fill="both", expand=True)

        ttk.Label(
            outer,
            text="Mouse Jiggler",
            style="Title.TLabel",
        ).pack(anchor="w")

        ttk.Label(
            outer,
            text="Keep your computer active with natural randomized mouse movement.",
            style="Subtitle.TLabel",
            wraplength=380,
        ).pack(anchor="w", pady=(4, 18))

        settings = ttk.LabelFrame(
            outer,
            text="Settings",
            style="Card.TLabelframe",
        )
        settings.pack(fill="x")

        self._field(settings, "Maximum delay (seconds)", self.max_delay, 0)
        self._field(settings, "Runtime (minutes)", self.duration, 1)

        timer = ttk.Frame(outer, padding=(0, 18, 0, 8))
        timer.pack(fill="x")

        ttk.Label(
            timer,
            text="TIME REMAINING",
            font=("Segoe UI", 8, "bold"),
        ).pack()

        ttk.Label(
            timer,
            textvariable=self.time_left,
            font=("Segoe UI", 28, "bold"),
        ).pack(pady=(2, 0))

        ttk.Label(
            outer,
            textvariable=self.status,
            style="Status.TLabel",
        ).pack(pady=(0, 12))

        # Give the control row a fixed height so the buttons remain visible.
        buttons = ttk.Frame(outer, height=48)
        buttons.pack(fill="x", pady=(0, 4))
        buttons.pack_propagate(False)

        self.start_button = ttk.Button(
            buttons,
            text="Start",
            style="Primary.TButton",
            command=self._start,
        )
        self.start_button.pack(
            side="left",
            expand=True,
            fill="both",
            padx=(0, 5),
        )

        self.pause_button = ttk.Button(
            buttons,
            text="Pause",
            command=self._pause_resume,
            state="disabled",
        )
        self.pause_button.pack(
            side="left",
            expand=True,
            fill="both",
            padx=5,
        )

        self.stop_button = ttk.Button(
            buttons,
            text="Stop",
            command=self._stop,
            state="disabled",
        )
        self.stop_button.pack(
            side="left",
            expand=True,
            fill="both",
            padx=(5, 0),
        )

        ttk.Label(
            outer,
            text="Pause freezes the timer and movement. Resume continues from where you paused.",
            style="Subtitle.TLabel",
            wraplength=380,
            justify="center",
        ).pack(pady=(16, 0))

    def _field(
        self,
        parent: ttk.Widget,
        label: str,
        variable: tk.StringVar,
        row: int,
    ) -> None:
        ttk.Label(parent, text=label).grid(
            row=row,
            column=0,
            sticky="w",
            pady=7,
        )

        entry = ttk.Entry(parent, textvariable=variable, width=12)
        entry.grid(row=row, column=1, sticky="e", pady=7)
        parent.columnconfigure(0, weight=1)

    def _start(self) -> None:
        try:
            max_delay = float(self.max_delay.get())
            duration = float(self.duration.get())
            if max_delay <= 0 or duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid settings",
                "Enter positive numbers for delay and runtime.",
            )
            return

        self.jiggler.start(
            JigglerConfig(
                max_delay=max_delay,
                duration_minutes=duration,
            )
        )
        self._update_controls(True, False)

    def _pause_resume(self) -> None:
        if self.jiggler.paused:
            self.jiggler.resume()
            self.pause_button.configure(text="Pause")
        else:
            self.jiggler.pause()
            self.pause_button.configure(text="Resume")

    def _stop(self) -> None:
        self.jiggler.stop()

    def _on_status(self, message: str) -> None:
        self.root.after(0, lambda: self.status.set(message))

        if message in {"Stopped.", "Finished.", "Ready."}:
            self.root.after(
                0,
                lambda: self._update_controls(False, False),
            )

    def _update_controls(self, running: bool, paused: bool) -> None:
        state = "normal" if running else "disabled"

        self.start_button.configure(
            state="disabled" if running else "normal"
        )
        self.pause_button.configure(
            state=state,
            text="Resume" if paused else "Pause",
        )
        self.stop_button.configure(state=state)

    def _refresh(self) -> None:
        if self.jiggler.running:
            total = float(self.duration.get()) * 60.0
            remaining = max(
                0.0,
                total - self.jiggler.elapsed_seconds(),
            )

            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            seconds = int(remaining % 60)

            self.time_left.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            self._update_controls(True, self.jiggler.paused)
        else:
            self.time_left.set("00:00:00")

        self.root.after(250, self._refresh)

    def _close(self) -> None:
        if self.jiggler.running:
            self.jiggler.stop()

        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()
