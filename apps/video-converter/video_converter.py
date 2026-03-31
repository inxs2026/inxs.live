import os
import shutil
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


SUPPORTED_FORMATS = ["mp4", "mkv", "avi", "mov", "webm", "flv", "wmv", "m4v"]
BASE_DIR = Path(__file__).resolve().parent


def parse_progress_timestamp(raw_value: str) -> int | None:
    value = raw_value.strip()
    if not value or value.upper() == "N/A":
        return None

    try:
        return int(value)
    except ValueError:
        return None


def resolve_download_dir() -> Path:
    preferred = Path.home() / "Downloads"
    fallback = BASE_DIR / "downloads"

    for candidate in (preferred, fallback):
        try:
            candidate.mkdir(parents=True, exist_ok=True)
        except OSError:
            continue

        if os.access(candidate, os.W_OK):
            return candidate

    raise RuntimeError("No writable output directory is available.")


def get_unique_output_path(downloads_dir: Path, base_name: str, output_format: str) -> Path:
    candidate = downloads_dir / f"{base_name}_converted.{output_format}"
    if not candidate.exists():
        return candidate

    idx = 1
    while True:
        candidate = downloads_dir / f"{base_name}_converted_{idx}.{output_format}"
        if not candidate.exists():
            return candidate
        idx += 1


def missing_dependencies() -> list[str]:
    return [name for name in ("ffmpeg", "ffprobe") if shutil.which(name) is None]


class VideoConverterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Video Converter")
        self.root.geometry("680x300")
        self.root.resizable(False, False)

        self.input_path_var = tk.StringVar()
        self.input_format_var = tk.StringVar(value=SUPPORTED_FORMATS[0])
        self.output_format_var = tk.StringVar(value=SUPPORTED_FORMATS[1])
        self.status_var = tk.StringVar(value="Select a video file to begin.")

        self.progress_var = tk.DoubleVar(value=0.0)
        self.is_converting = False

        self.downloads_dir = resolve_download_dir()

        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Input video").grid(row=0, column=0, sticky="w")

        input_entry = ttk.Entry(frame, textvariable=self.input_path_var, width=68)
        input_entry.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(4, 8))

        ttk.Button(frame, text="Browse", command=self.pick_input_file).grid(
            row=1, column=3, padx=(8, 0), sticky="ew"
        )

        ttk.Label(frame, text="From format").grid(row=2, column=0, sticky="w")
        self.input_combo = ttk.Combobox(
            frame,
            textvariable=self.input_format_var,
            values=SUPPORTED_FORMATS,
            state="readonly",
            width=20,
        )
        self.input_combo.grid(row=3, column=0, sticky="w", pady=(4, 8))

        ttk.Label(frame, text="To format").grid(row=2, column=1, sticky="w")
        self.output_combo = ttk.Combobox(
            frame,
            textvariable=self.output_format_var,
            values=SUPPORTED_FORMATS,
            state="readonly",
            width=20,
        )
        self.output_combo.grid(row=3, column=1, sticky="w", pady=(4, 8))

        self.convert_button = ttk.Button(frame, text="Convert", command=self.start_conversion)
        self.convert_button.grid(row=3, column=3, sticky="ew")

        self.progress_bar = ttk.Progressbar(
            frame, orient="horizontal", mode="determinate", variable=self.progress_var, maximum=100
        )
        self.progress_bar.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(12, 4))

        ttk.Label(frame, textvariable=self.status_var, anchor="w").grid(
            row=5, column=0, columnspan=4, sticky="ew", pady=(6, 0)
        )

        for col in range(4):
            frame.columnconfigure(col, weight=1)

    def pick_input_file(self) -> None:
        selected = filedialog.askopenfilename(
            title="Choose video file",
            filetypes=[
                (
                    "Video files",
                    "*.mp4 *.mkv *.avi *.mov *.webm *.flv *.wmv *.m4v *.mpeg *.mpg *.3gp *.ts",
                ),
                ("All files", "*.*"),
            ],
        )
        if not selected:
            return

        self.input_path_var.set(selected)
        suffix = Path(selected).suffix.lower().lstrip(".")
        if suffix in SUPPORTED_FORMATS:
            self.input_format_var.set(suffix)

        self.status_var.set("Ready to convert.")

    def _probe_duration_seconds(self, input_path: Path) -> float:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(input_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Failed to probe video duration.")

        try:
            return max(float(result.stdout.strip()), 0.0)
        except ValueError as exc:
            raise RuntimeError("Could not parse video duration.") from exc

    def start_conversion(self) -> None:
        if self.is_converting:
            return

        input_path = Path(self.input_path_var.get().strip()).expanduser()
        output_fmt = self.output_format_var.get().strip().lower()
        missing = missing_dependencies()

        if not input_path.exists() or not input_path.is_file():
            messagebox.showerror("Error", "Please select a valid input file.")
            return

        if output_fmt not in SUPPORTED_FORMATS:
            messagebox.showerror("Error", "Please select a valid output format.")
            return

        if missing:
            messagebox.showerror(
                "Error",
                f"Missing required dependencies: {', '.join(missing)}",
            )
            return

        output_path = get_unique_output_path(self.downloads_dir, input_path.stem, output_fmt)

        if input_path.suffix.lower().lstrip(".") == output_fmt:
            should_continue = messagebox.askyesno(
                "Same format selected",
                "Input and output formats are the same. Continue anyway?",
            )
            if not should_continue:
                return

        self.is_converting = True
        self.progress_var.set(0)
        self.progress_bar.configure(mode="determinate")
        self.status_var.set(f"Converting to {output_path.name}...")
        self.convert_button.configure(state="disabled")

        thread = threading.Thread(
            target=self._run_conversion,
            args=(input_path, output_path),
            daemon=True,
        )
        thread.start()

    def _run_conversion(self, input_path: Path, output_path: Path) -> None:
        try:
            duration_seconds = self._probe_duration_seconds(input_path)

            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(input_path),
                "-progress",
                "pipe:1",
                "-nostats",
                str(output_path),
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True,
                bufsize=1,
            )

            assert process.stdout is not None
            for line in process.stdout:
                if not line:
                    continue

                line = line.strip()
                if line.startswith("out_time_ms=") and duration_seconds > 0:
                    out_time_ms = parse_progress_timestamp(line.split("=", 1)[1])
                    if out_time_ms is None:
                        continue
                    percent = min((out_time_ms / (duration_seconds * 1_000_000)) * 100, 100)
                    self.root.after(0, self.progress_var.set, percent)
                elif line.startswith("progress=end"):
                    self.root.after(0, self.progress_var.set, 100)

            process.wait()
            if process.returncode != 0:
                raise RuntimeError("ffmpeg failed during conversion.")

            self.root.after(0, self._conversion_done, output_path)

        except Exception as exc:
            self.root.after(0, self._conversion_failed, str(exc))

    def _conversion_done(self, output_path: Path) -> None:
        self.is_converting = False
        self.convert_button.configure(state="normal")
        self.status_var.set(f"Done. Saved to: {output_path}")
        messagebox.showinfo("Success", f"Converted video saved to:\n{output_path}")

    def _conversion_failed(self, reason: str) -> None:
        self.is_converting = False
        self.convert_button.configure(state="normal")
        self.status_var.set("Conversion failed.")
        messagebox.showerror("Conversion failed", reason)


def main() -> None:
    root = tk.Tk()
    app = VideoConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
