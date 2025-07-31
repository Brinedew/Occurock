#!/usr/bin/env python3
"""
Occurock - PDF to Markdown Converter
Double-click to run - no terminal needed!
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import base64
import json
import requests
import threading
from pathlib import Path
import os

class OccurockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Occurock - PDF to Markdown Converter")
        self.root.geometry("800x600")
        self.root.configure(bg="#f8f9fa")  # Light neutral background
        
        # Professional color palette (2025 trends - 60-30-10 rule)
        self.colors = {
            'primary_bg': "#f8f9fa",      # Light neutral (60%)
            'secondary_bg': "#e9ecef",    # Slightly darker neutral (30%) 
            'accent': "#0d6efd",          # Professional blue (10%)
            'text_primary': "#212529",    # Dark gray text
            'text_secondary': "#6c757d",  # Medium gray text
            'success': "#198754",         # Professional green
            'text_area': "#ffffff"        # White for text areas
        }
        
        # Configure professional theme
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background=self.colors['primary_bg'], foreground=self.colors['text_primary'])
        style.configure("TButton", background=self.colors['accent'], foreground="white", font=("Arial", 9, "bold"))
        style.configure("TFrame", background=self.colors['primary_bg'])
        style.configure("TLabelFrame", background=self.colors['primary_bg'], foreground=self.colors['text_primary'])
        style.configure("TLabelFrame.Label", background=self.colors['primary_bg'], foreground=self.colors['text_secondary'], font=("Arial", 9, "bold"))
        style.configure("TEntry", background="white", foreground=self.colors['text_primary'], borderwidth=1)
        
        self.api_key = ""
        self.current_file = None
        self.result_text = ""
        
        self.create_widgets()
        self.load_settings()
        
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ttk.Label(header_frame, text="Occurock", font=("Arial", 24, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Convert PDFs to Markdown with AI-powered OCR")
        subtitle_label.pack()
        
        # API Key Section
        api_frame = ttk.LabelFrame(self.root, text="Configuration", padding=15)
        api_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(api_frame, text="Mistral API Key:").pack(anchor="w")
        self.api_key_entry = ttk.Entry(api_frame, width=60, show="*")
        self.api_key_entry.pack(fill="x", pady=(5, 10))
        self.api_key_entry.bind("<KeyRelease>", self.on_api_key_change)
        
        ttk.Label(api_frame, text="Output Folder:").pack(anchor="w")
        output_frame = ttk.Frame(api_frame)
        output_frame.pack(fill="x")
        
        self.output_entry = ttk.Entry(output_frame)
        self.output_entry.pack(side="left", fill="x", expand=True)
        self.output_entry.insert(0, "./output")
        
        ttk.Button(output_frame, text="Browse", command=self.browse_output_folder).pack(side="right", padx=(5, 0))
        
        # File Selection Section
        file_frame = ttk.LabelFrame(self.root, text="PDF File", padding=15)
        file_frame.pack(fill="x", padx=20, pady=10)
        
        self.file_label = ttk.Label(file_frame, text="No file selected", foreground=self.colors['text_secondary'])
        self.file_label.pack(anchor="w")
        
        ttk.Button(file_frame, text="Select PDF File", command=self.select_file).pack(pady=(10, 0))
        
        # Process Button
        self.process_button = ttk.Button(self.root, text="Convert to Markdown", command=self.start_processing)
        self.process_button.pack(pady=20)
        
        # Progress Section
        self.progress_frame = ttk.Frame(self.root)
        self.progress_frame.pack(fill="x", padx=20)
        
        self.progress_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.progress_frame, textvariable=self.progress_var)
        self.status_label.pack()
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill="x", pady=(5, 0))
        
        # Results Section
        results_frame = ttk.LabelFrame(self.root, text="Results", padding=15)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        button_frame = ttk.Frame(results_frame)
        button_frame.pack(fill="x", pady=(0, 10))
        
        self.save_button = ttk.Button(button_frame, text="Save Markdown", command=self.save_result, state="disabled")
        self.save_button.pack(side="left")
        
        self.copy_button = ttk.Button(button_frame, text="Copy to Clipboard", command=self.copy_result, state="disabled")
        self.copy_button.pack(side="left", padx=(10, 0))
        
        self.result_text_widget = scrolledtext.ScrolledText(
            results_frame, height=15, 
            bg=self.colors['text_area'], 
            fg=self.colors['text_primary'], 
            insertbackground=self.colors['text_primary'],
            borderwidth=1,
            relief="solid"
        )
        self.result_text_widget.pack(fill="both", expand=True)
        
    def browse_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)
            
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            self.file_label.config(text=Path(file_path).name, foreground=self.colors['success'])
            
    def on_api_key_change(self, event=None):
        self.api_key = self.api_key_entry.get()
        self.save_settings()
        
    def load_settings(self):
        settings_file = Path(__file__).parent / "settings.json"
        try:
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.api_key_entry.insert(0, settings.get('api_key', ''))
                    self.output_entry.delete(0, tk.END)
                    self.output_entry.insert(0, settings.get('output_folder', './output'))
        except Exception:
            pass
            
    def save_settings(self):
        settings_file = Path(__file__).parent / "settings.json"
        try:
            settings = {
                'api_key': self.api_key,
                'output_folder': self.output_entry.get()
            }
            with open(settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception:
            pass
            
    def start_processing(self):
        if not self.current_file:
            messagebox.showerror("Error", "Please select a PDF file first.")
            return
            
        if not self.api_key.strip():
            messagebox.showerror("Error", "Please enter your Mistral API key.")
            return
            
        # Start processing in background thread
        self.process_button.config(state="disabled")
        self.progress_bar.config(value=0)
        
        thread = threading.Thread(target=self.process_file)
        thread.daemon = True
        thread.start()
        
    def process_file(self):
        try:
            self.update_progress("Converting PDF to base64...", 20)
            
            # Read and encode PDF
            with open(self.current_file, 'rb') as f:
                pdf_data = f.read()
            
            base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
            data_uri = f"data:application/pdf;base64,{base64_pdf}"
            
            self.update_progress("Sending to Mistral OCR API...", 40)
            
            # Make API request
            response = requests.post(
                'https://api.mistral.ai/v1/ocr',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                },
                json={
                    'model': 'mistral-ocr-latest',
                    'document': {
                        'type': 'document_url',
                        'document_url': data_uri
                    },
                    'include_image_base64': True
                },
                timeout=300  # 5 minute timeout
            )
            
            self.update_progress("Processing response...", 80)
            
            if not response.ok:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                raise Exception(f"API Error {response.status_code}: {error_data.get('message', 'Unknown error')}")
            
            result = response.json()
            
            # Process pages
            extracted_text = ""
            image_count = 0
            
            if result.get('pages') and isinstance(result['pages'], list):
                for i, page in enumerate(result['pages'], 1):
                    extracted_text += f"\n\n--- PAGE {i} ---\n\n"
                    
                    if page.get('markdown'):
                        extracted_text += page['markdown']
                    elif page.get('text'):
                        extracted_text += page['text']
                    
                    if page.get('images'):
                        image_count += len(page['images'])
            else:
                extracted_text = f"Unexpected response structure:\n\n{json.dumps(result, indent=2)}"
            
            self.result_text = extracted_text.strip()
            
            self.update_progress(f"Complete! Processed {len(result.get('pages', []))} pages, {image_count} images", 100)
            
            # Update UI in main thread
            self.root.after(0, self.show_results)
            
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                error_msg = "Request timed out. The PDF might be too large or complex."
            elif "401" in error_msg:
                error_msg = "Invalid API key. Please check your Mistral API key."
            elif "429" in error_msg:
                error_msg = "Rate limit exceeded. Please wait and try again."
                
            self.root.after(0, lambda: self.show_error(error_msg))
            
    def update_progress(self, message, value):
        self.root.after(0, lambda: [
            self.progress_var.set(message),
            self.progress_bar.config(value=value)
        ])
        
    def show_results(self):
        self.result_text_widget.delete(1.0, tk.END)
        self.result_text_widget.insert(1.0, self.result_text)
        self.save_button.config(state="normal")
        self.copy_button.config(state="normal")
        self.process_button.config(state="normal")
        
    def show_error(self, error_msg):
        messagebox.showerror("OCR Failed", f"Error: {error_msg}")
        self.progress_var.set("Error occurred")
        self.process_button.config(state="normal")
        
    def save_result(self):
        if not self.result_text:
            return
            
        output_folder = Path(self.output_entry.get())
        output_folder.mkdir(exist_ok=True)
        
        filename = Path(self.current_file).stem + ".md"
        filepath = output_folder / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.result_text)
            messagebox.showinfo("Success", f"Markdown saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")
            
    def copy_result(self):
        if not self.result_text:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.result_text)
        messagebox.showinfo("Copied", "Text copied to clipboard!")

def main():
    root = tk.Tk()
    app = OccurockApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()