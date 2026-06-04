"""Tkinter UI cho QR generator."""

from __future__ import annotations

import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from qrgen.core import generate


class QRApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("QR Code Generator - Xe")
        root.geometry("560x340")
        root.minsize(500, 320)

        self.excel_path = tk.StringVar()
        self.subdomain = tk.StringVar(value="qr-xe")
        self.output_dir = tk.StringVar()
        self.status = tk.StringVar(value="Sẵn sàng.")
        self.progress_val = tk.DoubleVar(value=0.0)

        self.dist_dir: Path | None = None
        self.pdf_path: Path | None = None
        self._msg_queue: queue.Queue = queue.Queue()

        self._build_ui()
        self.root.after(100, self._poll_queue)

    def _build_ui(self) -> None:
        pad = {"padx": 12, "pady": 6}
        frm = ttk.Frame(self.root, padding=12)
        frm.pack(fill="both", expand=True)
        frm.columnconfigure(1, weight=1)

        ttk.Label(frm, text="File Excel:").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.excel_path).grid(row=0, column=1, sticky="ew", **pad)
        ttk.Button(frm, text="Chọn...", command=self._pick_excel).grid(row=0, column=2, **pad)

        ttk.Label(frm, text="Subdomain Netlify:").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.subdomain).grid(row=1, column=1, sticky="ew", **pad)
        ttk.Label(frm, text=".netlify.app", foreground="#666").grid(row=1, column=2, sticky="w", **pad)

        ttk.Label(frm, text="Thư mục xuất:").grid(row=2, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.output_dir).grid(row=2, column=1, sticky="ew", **pad)
        ttk.Button(frm, text="Chọn...", command=self._pick_output).grid(row=2, column=2, **pad)

        self.run_btn = ttk.Button(frm, text="Tạo QR Code", command=self._on_run)
        self.run_btn.grid(row=3, column=0, columnspan=3, pady=12)

        self.pbar = ttk.Progressbar(
            frm, orient="horizontal", mode="determinate",
            variable=self.progress_val, maximum=100,
        )
        self.pbar.grid(row=4, column=0, columnspan=3, sticky="ew", **pad)

        ttk.Label(frm, textvariable=self.status, foreground="#333").grid(
            row=5, column=0, columnspan=3, sticky="w", **pad,
        )

        result_frm = ttk.Frame(frm)
        result_frm.grid(row=6, column=0, columnspan=3, pady=(8, 0))
        self.open_dist_btn = ttk.Button(
            result_frm, text="Mở thư mục dist", command=self._open_dist, state="disabled",
        )
        self.open_dist_btn.pack(side="left", padx=6)
        self.open_pdf_btn = ttk.Button(
            result_frm, text="Mở PDF", command=self._open_pdf, state="disabled",
        )
        self.open_pdf_btn.pack(side="left", padx=6)
        self.open_netlify_btn = ttk.Button(
            result_frm, text="Mở Netlify Drop", command=self._open_netlify, state="disabled",
        )
        self.open_netlify_btn.pack(side="left", padx=6)

    def _pick_excel(self) -> None:
        path = filedialog.askopenfilename(
            title="Chọn file Excel",
            filetypes=[("Excel files", "*.xlsx *.xlsm"), ("All files", "*.*")],
        )
        if path:
            self.excel_path.set(path)
            if not self.output_dir.get():
                self.output_dir.set(str(Path(path).parent))

    def _pick_output(self) -> None:
        path = filedialog.askdirectory(title="Chọn thư mục xuất")
        if path:
            self.output_dir.set(path)

    def _on_run(self) -> None:
        xlsx = self.excel_path.get().strip()
        out_dir = self.output_dir.get().strip()
        sub = self.subdomain.get().strip()

        if not xlsx or not Path(xlsx).is_file():
            messagebox.showerror("Lỗi", "Chưa chọn file Excel hoặc file không tồn tại.")
            return
        if not out_dir:
            messagebox.showerror("Lỗi", "Chưa chọn thư mục xuất.")
            return
        if not sub:
            messagebox.showerror("Lỗi", "Chưa nhập tên subdomain Netlify.")
            return

        self.run_btn.config(state="disabled")
        self.open_dist_btn.config(state="disabled")
        self.open_pdf_btn.config(state="disabled")
        self.open_netlify_btn.config(state="disabled")
        self.progress_val.set(0)
        self.status.set("Bắt đầu...")

        threading.Thread(
            target=self._worker,
            args=(Path(xlsx), Path(out_dir), sub),
            daemon=True,
        ).start()

    def _worker(self, xlsx: Path, out_dir: Path, sub: str) -> None:
        def progress(cur: int, total: int, msg: str) -> None:
            pct = (cur / total * 100) if total else 0
            self._msg_queue.put(("progress", pct, msg))

        try:
            dist_dir, pdf_path, count = generate(xlsx, out_dir, sub, progress)
            self._msg_queue.put(("done", str(dist_dir), str(pdf_path), count))
        except Exception as e:
            self._msg_queue.put(("error", str(e)))

    def _poll_queue(self) -> None:
        try:
            while True:
                msg = self._msg_queue.get_nowait()
                kind = msg[0]
                if kind == "progress":
                    _, pct, status = msg
                    self.progress_val.set(pct)
                    self.status.set(status)
                elif kind == "done":
                    _, dist, pdf, count = msg
                    self.dist_dir = Path(dist)
                    self.pdf_path = Path(pdf)
                    self.progress_val.set(100)
                    self.status.set(f"Hoàn thành! {count} xe được tạo.")
                    self.run_btn.config(state="normal")
                    self.open_dist_btn.config(state="normal")
                    self.open_pdf_btn.config(state="normal")
                    self.open_netlify_btn.config(state="normal")
                elif kind == "error":
                    self.run_btn.config(state="normal")
                    self.status.set("Lỗi.")
                    messagebox.showerror("Lỗi", msg[1])
        except queue.Empty:
            pass
        self.root.after(100, self._poll_queue)

    @staticmethod
    def _open(path: str) -> None:
        if sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        elif sys.platform == "win32":
            import os
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", path], check=False)

    def _open_dist(self) -> None:
        if self.dist_dir:
            self._open(str(self.dist_dir))

    def _open_pdf(self) -> None:
        if self.pdf_path:
            self._open(str(self.pdf_path))

    def _open_netlify(self) -> None:
        self._open("https://app.netlify.com/drop")


def main() -> None:
    root = tk.Tk()
    try:
        # Slightly nicer ttk theme on each OS
        style = ttk.Style()
        for theme in ("aqua", "vista", "clam"):
            if theme in style.theme_names():
                style.theme_use(theme)
                break
    except tk.TclError:
        pass
    QRApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
