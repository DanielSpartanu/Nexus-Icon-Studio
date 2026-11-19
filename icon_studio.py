import os
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk, ImageOps

THEME = {
    "bg_dark": "#11111B",
    "bg_main": "#1E1E2E",
    "bg_card": "#262637",
    "bg_hover": "#313244",
    "border": "#45475A",
    "text_main": "#CDD6F4",
    "text_sub": "#A6ADC8",
    "accent_cyan": "#89DCEB",
    "accent_blue": "#89B4FA",
    "accent_green": "#A6E3A1",
    "accent_purple": "#CBA6F7",
    "accent_yellow": "#F9E2AF",
}

# Portability fix: dynamically resolve the user's Downloads directory on any Windows PC
DEFAULT_ICONS_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "Nexus_Icons")


class NexusStudioApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Nexus Icon & EXE Builder Studio")
        self.root.geometry("680x700")
        self.root.resizable(False, False)
        self.root.configure(bg=THEME["bg_dark"])

        os.makedirs(DEFAULT_ICONS_DIR, exist_ok=True)

        # State Tab 1 (Icon)
        self.selected_img_path = None
        self.preview_photo = None
        self.last_generated_ico = None
        self.var_crop_square = tk.BooleanVar(value=True)
        self.var_save_default_dir = tk.BooleanVar(value=True)

        # State Tab 2 (EXE Builder)
        self.selected_py_path = None
        self.selected_ico_for_exe = None
        self.var_exe_name = tk.StringVar()
        self.var_windowed = tk.BooleanVar(value=True)
        self.var_uac_admin = tk.BooleanVar(value=False)
        self.var_clean_temp = tk.BooleanVar(value=True)
        self.building_exe = False

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TNotebook", background=THEME["bg_dark"], borderwidth=0, tabmargins=[8, 6, 8, 0])
        style.configure(
            "TNotebook.Tab",
            background=THEME["bg_card"],
            foreground=THEME["text_sub"],
            padding=[16, 9],
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", THEME["bg_main"]), ("active", THEME["bg_hover"])],
            foreground=[("selected", THEME["accent_cyan"]), ("active", THEME["text_main"])],
        )

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=THEME["bg_dark"], pady=14)
        header.pack(fill="x")
        tk.Label(
            header,
            text="⚡ NEXUS ICON & EXE BUILDER STUDIO",
            font=("Segoe UI", 16, "bold"),
            fg=THEME["accent_cyan"],
            bg=THEME["bg_dark"],
        ).pack()
        tk.Label(
            header,
            text="Create multi-resolution icons (.ICO) and compile Python applications into .EXE",
            font=("Segoe UI", 9),
            fg=THEME["text_sub"],
            bg=THEME["bg_dark"],
        ).pack(pady=(2, 0))

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.tab_icon = tk.Frame(self.notebook, bg=THEME["bg_main"], padx=22, pady=18)
        self.tab_exe = tk.Frame(self.notebook, bg=THEME["bg_main"], padx=22, pady=18)

        self.notebook.add(self.tab_icon, text="  🎨 1. Multi-Res .ICO Generator  ")
        self.notebook.add(self.tab_exe, text="  📦 2. Python to .EXE Compiler  ")

        self._build_tab_icon()
        self._build_tab_exe()

    # ==========================================================================
    # TAB 1: MULTI-RES .ICO GENERATOR
    # ==========================================================================
    def _build_tab_icon(self):
        preview_frame = tk.Frame(
            self.tab_icon,
            bg=THEME["bg_card"],
            width=220,
            height=220,
            highlightbackground=THEME["accent_purple"],
            highlightthickness=2,
        )
        preview_frame.pack(pady=(4, 12))
        preview_frame.pack_propagate(False)

        self.lbl_preview = tk.Label(
            preview_frame,
            text="No image selected\n\nChoose a PNG / JPG image\nfor 1:1 preview",
            font=("Segoe UI", 9),
            fg=THEME["text_sub"],
            bg=THEME["bg_card"],
            justify="center",
        )
        self.lbl_preview.pack(fill="both", expand=True)

        self.lbl_img_name = tk.Label(
            self.tab_icon,
            text="Image: -",
            font=("Consolas", 9),
            fg=THEME["accent_cyan"],
            bg=THEME["bg_main"],
        )
        self.lbl_img_name.pack(pady=(0, 10))

        btn_row = tk.Frame(self.tab_icon, bg=THEME["bg_main"])
        btn_row.pack(fill="x", pady=(0, 14))

        tk.Button(
            btn_row,
            text="📂 Choose Image (PNG / JPG / WEBP)",
            font=("Segoe UI", 10, "bold"),
            bg=THEME["bg_hover"],
            fg=THEME["text_main"],
            activebackground=THEME["accent_blue"],
            activeforeground=THEME["bg_dark"],
            relief="flat",
            pady=9,
            cursor="hand2",
            command=self.select_image,
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        tk.Button(
            btn_row,
            text="📁 Open Icons Folder",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["accent_yellow"],
            activebackground=THEME["bg_hover"],
            activeforeground=THEME["accent_yellow"],
            relief="flat",
            padx=12,
            pady=9,
            cursor="hand2",
            command=self.open_icons_folder,
        ).pack(side="right")

        # Options
        opt_frame = tk.Frame(self.tab_icon, bg=THEME["bg_card"], padx=14, pady=12)
        opt_frame.pack(fill="x", pady=(0, 16))

        tk.Checkbutton(
            opt_frame,
            text="Automatically crop 1:1 (Perfect square, no distortion)",
            variable=self.var_crop_square,
            font=("Segoe UI", 9),
            fg=THEME["text_main"],
            bg=THEME["bg_card"],
            selectcolor=THEME["bg_dark"],
            activebackground=THEME["bg_card"],
            activeforeground=THEME["accent_cyan"],
            command=self._update_preview,
        ).pack(anchor="w")

        tk.Checkbutton(
            opt_frame,
            text=f"Save directly to: {DEFAULT_ICONS_DIR}",
            variable=self.var_save_default_dir,
            font=("Segoe UI", 9),
            fg=THEME["accent_green"],
            bg=THEME["bg_card"],
            selectcolor=THEME["bg_dark"],
            activebackground=THEME["bg_card"],
            activeforeground=THEME["accent_green"],
        ).pack(anchor="w", pady=(6, 0))

        self.btn_convert_ico = tk.Button(
            self.tab_icon,
            text="⚡ GENERATE MULTI-RESOLUTION ICONS (.ICO)",
            font=("Segoe UI", 11, "bold"),
            bg=THEME["accent_green"],
            fg=THEME["bg_dark"],
            activebackground=THEME["accent_cyan"],
            activeforeground=THEME["bg_dark"],
            relief="flat",
            pady=12,
            cursor="hand2",
            state="disabled",
            command=self.convert_to_ico,
        )
        self.btn_convert_ico.pack(fill="x")

    def open_icons_folder(self):
        os.makedirs(DEFAULT_ICONS_DIR, exist_ok=True)
        subprocess.Popen(["explorer", DEFAULT_ICONS_DIR])

    def select_image(self):
        path = filedialog.askopenfilename(
            title="Select image for icon",
            filetypes=[("Supported Images", "*.png *.jpg *.jpeg *.webp *.bmp"), ("All Files", "*.*")],
        )
        if not path:
            return
        self.selected_img_path = path
        self.lbl_img_name.config(text=f"Image: {os.path.basename(path)}")
        self.btn_convert_ico.config(state="normal")
        self._update_preview()

    def _prepare_image(self) -> Image.Image:
        img = Image.open(self.selected_img_path).convert("RGBA")
        if self.var_crop_square.get():
            min_side = min(img.size)
            img = ImageOps.fit(img, (min_side, min_side), method=Image.Resampling.LANCZOS)
        return img

    def _update_preview(self):
        if not self.selected_img_path:
            return
        try:
            img = self._prepare_image()
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            self.preview_photo = ImageTk.PhotoImage(img)
            self.lbl_preview.config(image=self.preview_photo, text="")
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to load image:\n{e}")

    def convert_to_ico(self):
        if not self.selected_img_path:
            return
        try:
            img = self._prepare_image()
            base_name = os.path.splitext(os.path.basename(self.selected_img_path))[0] + ".ico"

            if self.var_save_default_dir.get():
                os.makedirs(DEFAULT_ICONS_DIR, exist_ok=True)
                out_path = os.path.join(DEFAULT_ICONS_DIR, base_name)
            else:
                out_path = filedialog.asksaveasfilename(
                    title="Save .ICO Icon",
                    initialdir=DEFAULT_ICONS_DIR,
                    initialfile=base_name,
                    defaultextension=".ico",
                    filetypes=[("Windows Icon", "*.ico")],
                )
                if not out_path:
                    return

            sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
            img.save(out_path, format="ICO", sizes=sizes)

            # Auto-fill icon in Tab 2 for convenience
            self.last_generated_ico = out_path
            self.selected_ico_for_exe = out_path
            self.lbl_exe_ico.config(text=f"Icon: {os.path.basename(out_path)}", fg=THEME["accent_green"])

            messagebox.showinfo(
                "Icon Saved!",
                f"The .ICO file has been saved to:\n{out_path}\n\n(Automatically selected in Tab 2 for .EXE compilation!)",
            )
        except Exception as e:
            messagebox.showerror("Conversion Error", f"Failed to create .ICO file:\n{e}")

    # ==========================================================================
    # TAB 2: PYTHON (.PY) -> EXECUTABLE (.EXE) COMPILER
    # ==========================================================================
    def _build_tab_exe(self):
        # Step 1: Select .py file
        step1 = tk.Frame(self.tab_exe, bg=THEME["bg_card"], padx=14, pady=12)
        step1.pack(fill="x", pady=(0, 10))

        tk.Label(step1, text="1. Select Python script (.py):", font=("Segoe UI", 10, "bold"), fg=THEME["accent_cyan"], bg=THEME["bg_card"]).pack(anchor="w")

        row1 = tk.Frame(step1, bg=THEME["bg_card"])
        row1.pack(fill="x", pady=(6, 0))

        self.lbl_py_file = tk.Label(row1, text="No .py script chosen", font=("Consolas", 9), fg=THEME["text_sub"], bg=THEME["bg_card"], anchor="w")
        self.lbl_py_file.pack(side="left", fill="x", expand=True)

        tk.Button(
            row1,
            text="🐍 Choose .PY File",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_hover"],
            fg=THEME["text_main"],
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.select_py_file,
        ).pack(side="right")

        # Step 2: Select .ico & Output Name
        step2 = tk.Frame(self.tab_exe, bg=THEME["bg_card"], padx=14, pady=12)
        step2.pack(fill="x", pady=(0, 10))

        tk.Label(step2, text="2. Icon (.ico) & Application Name:", font=("Segoe UI", 10, "bold"), fg=THEME["accent_purple"], bg=THEME["bg_card"]).pack(anchor="w")

        row2 = tk.Frame(step2, bg=THEME["bg_card"])
        row2.pack(fill="x", pady=(6, 8))

        self.lbl_exe_ico = tk.Label(row2, text="Icon: Default (no .ico)", font=("Consolas", 9), fg=THEME["text_sub"], bg=THEME["bg_card"], anchor="w")
        self.lbl_exe_ico.pack(side="left", fill="x", expand=True)

        tk.Button(
            row2,
            text="❌ None",
            font=("Segoe UI", 8, "bold"),
            bg=THEME["bg_dark"],
            fg=THEME["text_sub"],
            relief="flat",
            padx=8,
            pady=6,
            cursor="hand2",
            command=self.clear_exe_ico,
        ).pack(side="right", padx=(4, 0))

        tk.Button(
            row2,
            text="🎨 Choose .ICO",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_hover"],
            fg=THEME["text_main"],
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.select_ico_for_exe,
        ).pack(side="right")

        name_row = tk.Frame(step2, bg=THEME["bg_card"])
        name_row.pack(fill="x")
        tk.Label(name_row, text="Final .EXE Name:", font=("Segoe UI", 9, "bold"), fg=THEME["text_main"], bg=THEME["bg_card"]).pack(side="left")
        tk.Entry(
            name_row,
            textvariable=self.var_exe_name,
            font=("Consolas", 10),
            bg=THEME["bg_dark"],
            fg=THEME["accent_cyan"],
            insertbackground=THEME["accent_cyan"],
            relief="flat",
        ).pack(side="left", fill="x", expand=True, padx=(10, 0), ipady=4)

        # Step 3: Compilation Options
        step3 = tk.Frame(self.tab_exe, bg=THEME["bg_card"], padx=14, pady=10)
        step3.pack(fill="x", pady=(0, 12))

        tk.Checkbutton(
            step3,
            text="Hide black console (--windowed) — recommended for GUI apps",
            variable=self.var_windowed,
            font=("Segoe UI", 9),
            fg=THEME["text_main"],
            bg=THEME["bg_card"],
            selectcolor=THEME["bg_dark"],
            activebackground=THEME["bg_card"],
        ).pack(anchor="w")

        tk.Checkbutton(
            step3,
            text="Request Administrator privileges on startup (--uac-admin)",
            variable=self.var_uac_admin,
            font=("Segoe UI", 9),
            fg=THEME["text_main"],
            bg=THEME["bg_card"],
            selectcolor=THEME["bg_dark"],
            activebackground=THEME["bg_card"],
        ).pack(anchor="w", pady=(3, 0))

        tk.Checkbutton(
            step3,
            text="Automatically clean temporary folders (build/ and .spec) after compilation",
            variable=self.var_clean_temp,
            font=("Segoe UI", 9),
            fg=THEME["text_main"],
            bg=THEME["bg_card"],
            selectcolor=THEME["bg_dark"],
            activebackground=THEME["bg_card"],
        ).pack(anchor="w", pady=(3, 0))

        # Build Button
        self.btn_build_exe = tk.Button(
            self.tab_exe,
            text="🚀 COMPILE TO .EXE NOW",
            font=("Segoe UI", 11, "bold"),
            bg=THEME["accent_blue"],
            fg=THEME["bg_dark"],
            activebackground=THEME["accent_cyan"],
            activeforeground=THEME["bg_dark"],
            relief="flat",
            pady=11,
            cursor="hand2",
            state="disabled",
            command=self.start_build_exe,
        )
        self.btn_build_exe.pack(fill="x", pady=(0, 10))

        # Console Log
        self.exe_log = scrolledtext.ScrolledText(
            self.tab_exe,
            height=9,
            bg=THEME["bg_dark"],
            fg=THEME["text_main"],
            font=("Consolas", 8),
            relief="flat",
            wrap="word",
        )
        self.exe_log.pack(fill="both", expand=True)
        self.exe_log.insert("end", "[PyInstaller Ready] Choose a .py file and click 'Compile to .EXE'.\n")

    def select_py_file(self):
        path = filedialog.askopenfilename(
            title="Select Python script (.py)",
            filetypes=[("Python Script", "*.py"), ("All Files", "*.*")],
        )
        if not path:
            return
        self.selected_py_path = path
        self.lbl_py_file.config(text=os.path.basename(path), fg=THEME["accent_green"])
        default_name = os.path.splitext(os.path.basename(path))[0]
        self.var_exe_name.set(default_name)
        self.btn_build_exe.config(state="normal")

    def select_ico_for_exe(self):
        path = filedialog.askopenfilename(
            title="Select icon (.ico)",
            initialdir=DEFAULT_ICONS_DIR,
            filetypes=[("Windows Icon", "*.ico")],
        )
        if not path:
            return
        self.selected_ico_for_exe = path
        self.lbl_exe_ico.config(text=f"Icon: {os.path.basename(path)}", fg=THEME["accent_green"])

    def clear_exe_ico(self):
        self.selected_ico_for_exe = None
        self.lbl_exe_ico.config(text="Icon: Default (no .ico)", fg=THEME["text_sub"])

    def _append_exe_log(self, text: str):
        self.root.after(0, lambda: self._insert_log_safe(text))

    def _insert_log_safe(self, text: str):
        self.exe_log.insert("end", text)
        self.exe_log.see("end")

    def start_build_exe(self):
        if self.building_exe or not self.selected_py_path:
            return
        exe_name = self.var_exe_name.get().strip() or "MyApplication"
        self.building_exe = True
        self.btn_build_exe.config(state="disabled", text="⏳ BUILDING (Please wait ~15-30s)...")
        self.exe_log.delete("1.0", "end")
        threading.Thread(target=self._worker_build_exe, args=(exe_name,), daemon=True).start()

    def _worker_build_exe(self, exe_name: str):
        work_dir = os.path.dirname(self.selected_py_path)
        dist_dir = work_dir
        build_tmp = os.path.join(work_dir, "_pyinstaller_build_tmp")

        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            f"--distpath={dist_dir}",
            f"--workpath={build_tmp}",
            f"--specpath={build_tmp}",
            f"--name={exe_name}",
        ]

        if self.var_windowed.get():
            cmd.append("--windowed")
        if self.var_uac_admin.get():
            cmd.append("--uac-admin")
        if self.selected_ico_for_exe and os.path.exists(self.selected_ico_for_exe):
            cmd.append(f"--icon={self.selected_ico_for_exe}")

        cmd.append(self.selected_py_path)

        self._append_exe_log(f"Executed command:\n{' '.join(cmd)}\n\nBuilding executable...\n")

        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                startupinfo=startupinfo,
                creationflags=0x08000000,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            for line in proc.stdout:
                self._append_exe_log(line)

            proc.wait()

            if self.var_clean_temp.get() and os.path.exists(build_tmp):
                shutil.rmtree(build_tmp, ignore_errors=True)
                self._append_exe_log("\n[Cleanup] Temporary build folders have been removed.\n")

            final_exe = os.path.join(dist_dir, f"{exe_name}.exe")
            if proc.returncode == 0 and os.path.exists(final_exe):
                self._append_exe_log(f"\n✅ SUCCESS! Executable created at:\n{final_exe}\n")
                self.root.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Compilation Successful!",
                        f"The application has been packaged into an .EXE and saved right next to the script:\n\n{final_exe}",
                    ),
                )
            else:
                self._append_exe_log("\n❌ Compilation error. Check the log above.\n")
                self.root.after(0, lambda: messagebox.showerror("Compilation Error", "PyInstaller encountered an error. Check the console log."))
        except Exception as e:
            self._append_exe_log(f"\n❌ Exception: {e}\n")
        finally:
            self.building_exe = False
            self.root.after(0, lambda: self.btn_build_exe.config(state="normal", text="🚀 COMPILE TO .EXE NOW"))


if __name__ == "__main__":
    root = tk.Tk()
    app = NexusStudioApp(root)
    root.mainloop()