# pdf_gui.py
import os
import sys
import json
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import importlib.util

# Import analyze_pdf_folder.py dynamically
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "scripts", "analyze_pdf_folder.py")
spec = importlib.util.spec_from_file_location("analyze_pdf_folder", SCRIPT_PATH)
analyze_pdf_folder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyze_pdf_folder)

class PDFAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Local PDF Analyzer")

        self.pdf_dir = tk.StringVar()
        self.output_path = tk.StringVar()
        self.filter_images_only = tk.BooleanVar()
        self.results = []

        self.build_ui()

    def build_ui(self):
        frm = ttk.Frame(self.root, padding=12)
        frm.grid(sticky="nsew")

        ttk.Label(frm, text="Select PDF Folder:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.pdf_dir, width=50).grid(row=0, column=1, padx=4)
        ttk.Button(frm, text="Browse", command=self.pick_pdf_folder).grid(row=0, column=2)

        ttk.Label(frm, text="Save Results (optional):").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.output_path, width=50).grid(row=1, column=1, padx=4)
        ttk.Button(frm, text="Choose File", command=self.pick_output_file).grid(row=1, column=2)

        ttk.Checkbutton(frm, text="Only show image-only PDFs", variable=self.filter_images_only, command=self.refresh_table).grid(row=2, column=1, sticky="w", pady=4)

        ttk.Button(frm, text="Run Scan", command=self.start_scan).grid(row=3, column=1, pady=10)

        # Treeview for results
        self.tree = ttk.Treeview(frm, columns=("file", "pages", "text_pages", "image_only"), show="headings", height=12)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.grid(row=4, column=0, columnspan=3, sticky="nsew")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def pick_pdf_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.pdf_dir.set(folder)

    def pick_output_file(self):
        file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json"), ("CSV Files", "*.csv")])
        if file:
            self.output_path.set(file)

    def start_scan(self):
        if not self.pdf_dir.get():
            messagebox.showerror("Error", "Please select a folder of PDFs.")
            return
        threading.Thread(target=self.run_scan).start()

    def run_scan(self):
        self.results = analyze_pdf_folder.analyze_folder(self.pdf_dir.get())
        self.refresh_table()
        if self.output_path.get():
            self.save_results()

    def refresh_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for item in self.results:
            if self.filter_images_only.get() and not item.get("image_only"):
                continue
            self.tree.insert("", "end", values=(
                item.get("filename"),
                item.get("total_pages"),
                item.get("text_pages"),
                item.get("image_only")
            ))

    def save_results(self):
        try:
            with open(self.output_path.get(), "w") as f:
                if self.output_path.get().endswith(".csv"):
                    import csv
                    writer = csv.DictWriter(f, fieldnames=["filename", "total_pages", "text_pages", "image_only"])
                    writer.writeheader()
                    writer.writerows(self.results)
                else:
                    json.dump(self.results, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFAnalyzerApp(root)
    root.mainloop()
# This script provides a GUI for analyzing PDF files in a selected directory.
# It allows users to filter results, save them in JSON or CSV format, and run the analysis in a separate thread.
# The GUI is built using Tkinter, and the analysis is performed using a separate script.