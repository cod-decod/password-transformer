import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from datetime import datetime

from src.core.file_handler import FileHandler
from src.core.analyzer import PasswordAnalyzer
from src.core.transformer import PasswordTransformer
from src.utils.config import Config

class PasswordTransformerApp:
    def __init__(self):
        """Initialize the main application"""
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize components
        self.config = Config()
        self.file_handler = FileHandler()
        self.analyzer = PasswordAnalyzer()
        self.transformer = PasswordTransformer()
        
        # Initialize GUI
        self.setup_main_window()
        self.create_widgets()
        
        # Data storage
        self.input_data = []
        self.output_data = []
        self.input_file_path = ""
        
    def setup_main_window(self):
        """Setup the main application window"""
        self.root = ctk.CTk()
        self.root.title("🔐 Password Transformer - Intelligent Password Modifier")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
    def create_widgets(self):
        """Create and arrange GUI widgets"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="🔐 Password Transformer", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.grid(row=0, column=0, pady=(20, 20))
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.main_frame, 
            text="Intelligent Password Analysis & Transformation",
            font=ctk.CTkFont(size=14)
        )
        self.subtitle_label.grid(row=1, column=0, pady=(0, 20))
        
        # Create sections
        self.create_file_section()
        self.create_settings_section()
        self.create_preview_section()
        self.create_progress_section()
        self.create_action_buttons()
        
    def create_file_section(self):
        """Create file operations section"""
        file_frame = ctk.CTkFrame(self.main_frame)
        file_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        file_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        ctk.CTkLabel(
            file_frame, 
            text="📁 File Selection", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=3, pady=(15, 10))
        
        # File selection
        ctk.CTkLabel(file_frame, text="Input File:").grid(
            row=1, column=0, padx=15, pady=10, sticky="w"
        )
        
        self.file_path_entry = ctk.CTkEntry(
            file_frame, 
            placeholder_text="Select email:password file...",
            height=35
        )
        self.file_path_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        self.browse_button = ctk.CTkButton(
            file_frame, 
            text="📂 Browse", 
            command=self.browse_file, 
            width=120,
            height=35
        )
        self.browse_button.grid(row=1, column=2, padx=15, pady=10)
        
        # File info
        self.file_info_label = ctk.CTkLabel(
            file_frame, 
            text="ℹ️ No file selected - Expected format: email:password (one per line)"
        )
        self.file_info_label.grid(row=2, column=0, columnspan=3, padx=15, pady=(5, 15))
        
    def create_settings_section(self):
        """Create transformation settings section"""
        settings_frame = ctk.CTkFrame(self.main_frame)
        settings_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        
        # Settings title
        ctk.CTkLabel(
            settings_frame, 
            text="⚙️ Transformation Settings", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=3, pady=(15, 20))
        
        # Create two columns for settings
        left_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        right_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        
        left_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        right_frame.grid(row=1, column=1, sticky="ew", padx=20, pady=10)
        
        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_columnconfigure(1, weight=1)
        
        # Left column settings
        ctk.CTkLabel(left_frame, text="Transformation Intensity:", 
                    font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", pady=(0,5))
        
        self.intensity_var = tk.StringVar(value="moderate")
        self.intensity_menu = ctk.CTkOptionMenu(
            left_frame,
            variable=self.intensity_var,
            values=["conservative", "moderate", "aggressive"],
            width=200
        )
        self.intensity_menu.grid(row=1, column=0, sticky="w", pady=(0,15))
        
        # Checkboxes in left column
        self.char_sub_var = tk.BooleanVar(value=True)
        self.char_sub_check = ctk.CTkCheckBox(
            left_frame, 
            text="🔤 Character Substitution (a→@, o→0, s→$)", 
            variable=self.char_sub_var
        )
        self.char_sub_check.grid(row=2, column=0, sticky="w", pady=5)
        
        self.add_year_var = tk.BooleanVar(value=True)
        self.add_year_check = ctk.CTkCheckBox(
            left_frame, 
            text="📅 Add Current Year (2024)", 
            variable=self.add_year_var
        )
        self.add_year_check.grid(row=3, column=0, sticky="w", pady=5)
        
        # Right column settings
        ctk.CTkLabel(right_frame, text="Advanced Options:", 
                    font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", pady=(0,5))
        
        self.intelligent_var = tk.BooleanVar(value=True)
        self.intelligent_check = ctk.CTkCheckBox(
            right_frame, 
            text="🧠 Intelligent Pattern Recognition", 
            variable=self.intelligent_var
        )
        self.intelligent_check.grid(row=1, column=0, sticky="w", pady=(15,5))
        
        self.preserve_var = tk.BooleanVar(value=True)
        self.preserve_check = ctk.CTkCheckBox(
            right_frame, 
            text="🛡️ Preserve Strong Passwords", 
            variable=self.preserve_var
        )
        self.preserve_check.grid(row=2, column=0, sticky="w", pady=5)
        
        self.increment_var = tk.BooleanVar(value=True)
        self.increment_check = ctk.CTkCheckBox(
            right_frame, 
            text="🔢 Smart Number Incrementing", 
            variable=self.increment_var
        )
        self.increment_check.grid(row=3, column=0, sticky="w", pady=5)
        
    def create_preview_section(self):
        """Create results preview section"""
        preview_frame = ctk.CTkFrame(self.main_frame)
        preview_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)
        preview_frame.grid_rowconfigure(1, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        
        # Preview title
        ctk.CTkLabel(
            preview_frame, 
            text="👁️ Preview Results", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, pady=(15, 10))
        
        # Create preview table
        columns = ("email", "original", "modified", "strength", "change")
        self.preview_tree = ttk.Treeview(
            preview_frame, 
            columns=columns,
            show="headings",
            height=12
        )
        
        # Configure columns
        self.preview_tree.heading("email", text="📧 Email")
        self.preview_tree.heading("original", text="🔒 Original Password")
        self.preview_tree.heading("modified", text="🔓 Modified Password")
        self.preview_tree.heading("strength", text="💪 Strength Score")
        self.preview_tree.heading("change", text="📊 Change")
        
        self.preview_tree.column("email", width=220)
        self.preview_tree.column("original", width=180)
        self.preview_tree.column("modified", width=180)
        self.preview_tree.column("strength", width=120)
        self.preview_tree.column("change", width=100)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_tree.yview)
        scrollbar_x = ttk.Scrollbar(preview_frame, orient="horizontal", command=self.preview_tree.xview)
        self.preview_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Grid layout
        self.preview_tree.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        scrollbar_y.grid(row=1, column=1, sticky="ns", pady=(0, 15))
        scrollbar_x.grid(row=2, column=0, sticky="ew", padx=15)
        
    def create_progress_section(self):
        """Create progress tracking section"""
        progress_frame = ctk.CTkFrame(self.main_frame)
        progress_frame.grid(row=5, column=0, sticky="ew", padx=10, pady=5)
        progress_frame.grid_columnconfigure(1, weight=1)
        
        # Progress elements
        self.progress_label = ctk.CTkLabel(
            progress_frame, 
            text="✅ Ready to process passwords",
            font=ctk.CTkFont(size=12)
        )
        self.progress_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame, 
            variable=self.progress_var,
            height=20
        )
        self.progress_bar.grid(row=0, column=1, padx=(10, 15), pady=15, sticky="ew")
        self.progress_bar.set(0)
        
    def create_action_buttons(self):
        """Create action buttons section"""
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.grid(row=6, column=0, sticky="ew", padx=10, pady=(5, 20))
        button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Main action buttons
        self.preview_button = ctk.CTkButton(
            button_frame, 
            text="👁️ Preview Changes", 
            command=self.preview_changes,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.preview_button.grid(row=0, column=0, padx=10, pady=15, sticky="ew")
        
        self.process_button = ctk.CTkButton(
            button_frame, 
            text="🔄 Transform Passwords", 
            command=self.process_passwords,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.process_button.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        self.export_button = ctk.CTkButton(
            button_frame, 
            text="💾 Export Results", 
            command=self.export_results, 
            state="disabled",
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.export_button.grid(row=0, column=2, padx=10, pady=15, sticky="ew")
        
        self.theme_button = ctk.CTkButton(
            button_frame, 
            text="🌙 Theme", 
            command=self.toggle_theme,
            height=45,
            width=120
        )
        self.theme_button.grid(row=0, column=3, padx=10, pady=15, sticky="ew")
        
    def browse_file(self):
        """Open file browser to select input file"""
        file_path = filedialog.askopenfilename(
            title="Select Password File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            self.input_file_path = file_path
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)
            
            try:
                self.input_data = self.file_handler.load_file(file_path)
                self.file_info_label.configure(
                    text=f"✅ Successfully loaded {len(self.input_data)} email:password pairs"
                )
                self.preview_button.configure(state="normal")
            except Exception as e:
                self.file_info_label.configure(
                    text=f"❌ Error loading file: {str(e)}"
                )
                messagebox.showerror("File Error", f"Could not load file:\n{str(e)}")
                
    def preview_changes(self):
        """Preview password transformations"""
        if not self.input_data:
            messagebox.showwarning("No Data", "Please select and load a file first.")
            return
            
        self.progress_label.configure(text="🔄 Generating preview...")
        self.progress_bar.set(0)
        
        # Clear existing preview
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
            
        # Process in thread
        threading.Thread(target=self._generate_preview, daemon=True).start()
        
    def _generate_preview(self):
        """Generate preview data in separate thread"""
        try:
            preview_data = []
            total = min(len(self.input_data), 100)  # Limit preview to 100 items
            
            for i in range(total):
                email, password = self.input_data[i]
                
                # Analyze current password
                analysis = self.analyzer.analyze_password(password)
                
                # Generate transformation
                settings = self._get_current_settings()
                new_password = self.transformer.transform_password(password, analysis, settings)
                
                # Analyze new password
                new_analysis = self.analyzer.analyze_password(new_password)
                
                # Calculate strength change
                strength_change = new_analysis['strength_score'] - analysis['strength_score']
                
                preview_data.append({
                    'email': email,
                    'original': password,
                    'modified': new_password,
                    'original_strength': analysis['strength_score'],
                    'new_strength': new_analysis['strength_score'],
                    'change': strength_change
                })
                
                # Update progress
                progress = (i + 1) / total
                self.root.after(0, lambda p=progress: self.progress_bar.set(p))
                
            # Update UI
            self.root.after(0, lambda: self._update_preview_ui(preview_data))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Preview Error", str(e)))
            
    def _update_preview_ui(self, preview_data):
        """Update preview UI with generated data"""
        for data in preview_data:
            # Truncate long passwords for display
            orig_display = data['original'] if len(data['original']) <= 15 else data['original'][:12] + "..."
            mod_display = data['modified'] if len(data['modified']) <= 15 else data['modified'][:12] + "..."
            
            # Format strength scores and change
            strength_text = f"{data['original_strength']:.1f} → {data['new_strength']:.1f}"
            change_text = f"{data['change']:+.1f}"
            
            self.preview_tree.insert("", "end", values=(
                data['email'], 
                orig_display, 
                mod_display, 
                strength_text,
                change_text
            ))
            
        total_shown = len(preview_data)
        total_available = len(self.input_data)
        
        if total_available > 100:
            self.progress_label.configure(
                text=f"📊 Preview showing first {total_shown} of {total_available} passwords"
            )
        else:
            self.progress_label.configure(
                text=f"📊 Preview generated for {total_shown} passwords"
            )
        self.progress_bar.set(1.0)
        
    def process_passwords(self):
        """Process all passwords and generate output"""
        if not self.input_data:
            messagebox.showwarning("No Data", "Please select and load a file first.")
            return
            
        # Ask for output location
        output_path = filedialog.asksaveasfilename(
            title="Save Transformed Passwords",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not output_path:
            return
            
        self.progress_label.configure(text="🔄 Processing passwords...")
        self.process_button.configure(state="disabled")
        self.progress_bar.set(0)
        
        # Process in thread
        threading.Thread(
            target=self._process_passwords_thread, 
            args=(output_path,), 
            daemon=True
        ).start()
        
    def _process_passwords_thread(self, output_path):
        """Process passwords in separate thread"""
        try:
            processed_data = []
            total = len(self.input_data)
            settings = self._get_current_settings()
            
            for i, (email, password) in enumerate(self.input_data):
                # Analyze password
                analysis = self.analyzer.analyze_password(password)
                
                # Transform password
                new_password = self.transformer.transform_password(password, analysis, settings)
                processed_data.append((email, new_password))
                
                # Update progress
                progress = (i + 1) / total
                self.root.after(0, lambda p=progress: self.progress_bar.set(p))
                
            # Save results
            if output_path.endswith('.csv'):
                self.file_handler.save_csv(output_path, processed_data)
            else:
                self.file_handler.save_file(output_path, processed_data)
                
            self.output_data = processed_data
            
            # Update UI
            self.root.after(0, lambda: self._processing_complete(len(processed_data), output_path))
            
        except Exception as e:
            self.root.after(0, lambda: self._processing_error(str(e)))
            
    def _processing_complete(self, count, output_path):
        """Handle successful processing completion"""
        self.progress_label.configure(
            text=f"✅ Successfully processed {count} passwords → {os.path.basename(output_path)}"
        )
        self.process_button.configure(state="normal")
        self.export_button.configure(state="normal")
        messagebox.showinfo(
            "Success", 
            f"🎉 Passwords processed successfully!\n\n"
            f"📊 {count} passwords transformed\n"
            f"💾 Saved to: {os.path.basename(output_path)}"
        )
        
    def _processing_error(self, error_msg):
        """Handle processing errors"""
        self.progress_label.configure(text="❌ Processing failed")
        self.process_button.configure(state="normal")
        self.progress_bar.set(0)
        messagebox.showerror("Processing Error", f"Failed to process passwords:\n{error_msg}")
        
    def export_results(self):
        """Export processing results"""
        if not self.output_data:
            messagebox.showwarning("No Results", "No processed data to export.")
            return
            
        output_path = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")]
        )
        
        if output_path:
            try:
                if output_path.endswith('.csv'):
                    self.file_handler.save_csv(output_path, self.output_data)
                else:
                    self.file_handler.save_file(output_path, self.output_data)
                messagebox.showinfo("Success", f"Results exported to:\n{os.path.basename(output_path)}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export:\n{str(e)}")
                
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        current = ctk.get_appearance_mode()
        new_mode = "light" if current == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        
        # Update theme button text
        icon = "☀️" if new_mode == "light" else "🌙"
        self.theme_button.configure(text=f"{icon} Theme")
        
    def _get_current_settings(self):
        """Get current transformation settings"""
        return {
            'intensity': self.intensity_var.get(),
            'character_substitution': self.char_sub_var.get(),
            'add_year': self.add_year_var.get(),
            'intelligent_patterns': self.intelligent_var.get(),
            'preserve_strong': self.preserve_var.get(),
            'increment_numbers': self.increment_var.get()
        }
        
    def run(self):
        """Start the application"""
        self.root.mainloop()
