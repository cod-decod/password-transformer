import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from datetime import datetime

from core.file_handler import FileHandler
from core.analyzer import PasswordAnalyzer
from core.transformer import PasswordTransformer
from utils.config import Config
from ml.analytics import Analytics

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
        
        # Initialize transformer with ML (with error handling)
        try:
            self.transformer = PasswordTransformer(enable_ml=True)
            self.ml_available = True
        except Exception as e:
            print(f"Warning: ML initialization failed, using basic mode: {e}")
            self.transformer = PasswordTransformer(enable_ml=False)
            self.ml_available = False
            
        # Initialize analytics (with error handling)
        try:
            self.analytics = Analytics()
        except Exception as e:
            print(f"Warning: Analytics initialization failed: {e}")
            self.analytics = None
        
        # Initialize GUI
        self.setup_main_window()
        self.create_widgets()
        
        # Data storage
        self.input_data = []
        self.output_data = []
        self.input_file_path = ""
        
        # ML and Smart Mode
        self.smart_mode_enabled = tk.BooleanVar(value=False)
        self.ml_insights_cache = None
        
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
        self.main_frame.grid_rowconfigure(2, weight=1)
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
            text="Intelligent Password Analysis & Transformation with ML",
            font=ctk.CTkFont(size=14)
        )
        self.subtitle_label.grid(row=1, column=0, pady=(0, 20))
        
        # Create tabbed interface
        self.tabview = ctk.CTkTabview(self.main_frame, width=1150, height=600)
        self.tabview.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        # Add tabs
        self.transformer_tab = self.tabview.add("🔧 Transformer")
        self.analytics_tab = self.tabview.add("📊 Analytics")
        self.smart_mode_tab = self.tabview.add("🧠 Smart Mode")
        
        # Configure tabs
        self.transformer_tab.grid_rowconfigure(2, weight=1)
        self.transformer_tab.grid_columnconfigure(0, weight=1)
        
        self.analytics_tab.grid_rowconfigure(1, weight=1)
        self.analytics_tab.grid_columnconfigure(0, weight=1)
        
        self.smart_mode_tab.grid_rowconfigure(1, weight=1)
        self.smart_mode_tab.grid_columnconfigure(0, weight=1)
        
        # Create sections in transformer tab
        self.create_transformer_tab_content()
        self.create_analytics_tab_content()
        self.create_smart_mode_tab_content()
        
    def create_transformer_tab_content(self):
        """Create content for the transformer tab"""
        self.create_file_section(self.transformer_tab)
        self.create_settings_section(self.transformer_tab)
        self.create_preview_section(self.transformer_tab)
        self.create_progress_section(self.transformer_tab)
        self.create_action_buttons(self.transformer_tab)
        
    def create_file_section(self, parent):
        """Create file operations section"""
        file_frame = ctk.CTkFrame(parent)
        file_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
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
        
    def create_settings_section(self, parent):
        """Create transformation settings section"""
        settings_frame = ctk.CTkFrame(parent)
        settings_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
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
        
    def create_preview_section(self, parent):
        """Create results preview section"""
        preview_frame = ctk.CTkFrame(parent)
        preview_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
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
        
    def create_progress_section(self, parent):
        """Create progress tracking section"""
        progress_frame = ctk.CTkFrame(parent)
        progress_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
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
        
    def create_action_buttons(self, parent):
        """Create action buttons section"""
        button_frame = ctk.CTkFrame(parent)
        button_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=(5, 20))
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
        """Generate preview data in separate thread with ML enhancement"""
        try:
            preview_data = []
            total = min(len(self.input_data), 100)  # Limit preview to 100 items
            settings = self._get_current_settings()
            
            for i in range(total):
                email, password = self.input_data[i]
                
                try:
                    # Analyze current password
                    analysis = self.analyzer.analyze_password(password)
                    
                    # Generate transformation with ML if available
                    if self.ml_available:
                        new_password = self.transformer.transform_password(
                            password, analysis, settings, email
                        )
                    else:
                        new_password = self.transformer.transform_password(password, analysis, settings)
                    
                    # Analyze new password
                    new_analysis = self.analyzer.analyze_password(new_password)
                    
                    # Calculate strength change
                    strength_change = new_analysis['strength_score'] - analysis['strength_score']
                    
                    # Get transformation summary
                    changes = self.transformer.get_transformation_summary(password, new_password, analysis)
                    
                    preview_data.append({
                        'email': email,
                        'original': password,
                        'modified': new_password,
                        'original_strength': analysis['strength_score'],
                        'new_strength': new_analysis['strength_score'],
                        'change': strength_change,
                        'pattern_type': analysis.get('pattern_type', 'unknown'),
                        'changes_applied': ', '.join(changes[:2])  # Show first 2 changes
                    })
                    
                except Exception as e:
                    print(f"Preview generation failed for {email}: {e}")
                    # Add error entry
                    preview_data.append({
                        'email': email,
                        'original': password,
                        'modified': '❌ Error',
                        'original_strength': 0,
                        'new_strength': 0,
                        'change': 0,
                        'pattern_type': 'error',
                        'changes_applied': 'Failed to process'
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
        """Process passwords in separate thread with enhanced error handling"""
        try:
            processed_data = []
            total = len(self.input_data)
            settings = self._get_current_settings()
            failed_transformations = 0
            
            for i, (email, password) in enumerate(self.input_data):
                try:
                    # Analyze password
                    analysis = self.analyzer.analyze_password(password)
                    
                    # Transform password with ML enhancement if available
                    if self.ml_available:
                        # Include email context for ML recommendations
                        new_password = self.transformer.transform_password(
                            password, analysis, settings, email
                        )
                        
                        # Learn from transformation if successful
                        new_analysis = self.analyzer.analyze_password(new_password)
                        if new_analysis['strength_score'] > analysis['strength_score']:
                            # Positive improvement - learn from it
                            self.transformer.learn_from_transformation(
                                password, new_password, analysis, new_analysis, 
                                settings, None, True, email
                            )
                    else:
                        # Basic transformation without ML
                        new_password = self.transformer.transform_password(password, analysis, settings)
                        
                    processed_data.append((email, new_password))
                    
                except Exception as e:
                    print(f"Warning: Failed to process {email}: {e}")
                    # Keep original password on error
                    processed_data.append((email, password))
                    failed_transformations += 1
                    
                # Update progress
                progress = (i + 1) / total
                self.root.after(0, lambda p=progress: self.progress_bar.set(p))
                
            # Save results with error handling
            try:
                if output_path.endswith('.csv'):
                    self.file_handler.save_csv(output_path, processed_data)
                else:
                    self.file_handler.save_file(output_path, processed_data)
                    
                self.output_data = processed_data
                
                # Create completion message
                success_count = len(processed_data) - failed_transformations
                completion_msg = f"Successfully processed {success_count}/{len(processed_data)} passwords"
                if failed_transformations > 0:
                    completion_msg += f" ({failed_transformations} failed)"
                
                # Update UI
                self.root.after(0, lambda: self._processing_complete(
                    success_count, output_path, failed_transformations
                ))
                
            except Exception as save_error:
                self.root.after(0, lambda: self._processing_error(f"Save failed: {save_error}"))
                
        except Exception as e:
            self.root.after(0, lambda: self._processing_error(str(e)))
            
    def _processing_complete(self, count, output_path, failed_count=0):
        """Handle successful processing completion with enhanced reporting"""
        status_text = f"✅ Successfully processed {count} passwords → {os.path.basename(output_path)}"
        if failed_count > 0:
            status_text += f" (⚠️ {failed_count} failed)"
            
        self.progress_label.configure(text=status_text)
        self.process_button.configure(state="normal")
        self.export_button.configure(state="normal")
        
        # Show detailed message
        message = f"🎉 Password processing completed!\\n\\n📊 {count} passwords transformed"
        if failed_count > 0:
            message += f"\\n⚠️ {failed_count} passwords failed to transform"
        message += f"\\n💾 Saved to: {os.path.basename(output_path)}"
        
        if self.ml_available:
            message += "\\n\\n🧠 ML system learned from successful transformations"
            
        messagebox.showinfo("Success", message)
        
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
        
    def create_analytics_tab_content(self):
        """Create content for the analytics tab"""
        # Analytics header
        header_frame = ctk.CTkFrame(self.analytics_tab)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            header_frame,
            text="📊 ML Analytics Dashboard",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # Refresh button
        self.refresh_analytics_button = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh Data",
            command=self.refresh_analytics,
            width=120
        )
        self.refresh_analytics_button.grid(row=0, column=1, padx=15, pady=15, sticky="e")
        
        # Main analytics content
        self.analytics_content_frame = ctk.CTkScrollableFrame(self.analytics_tab)
        self.analytics_content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.analytics_content_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize analytics display
        self.refresh_analytics()
        
    def create_smart_mode_tab_content(self):
        """Create content for the smart mode tab"""
        # Smart Mode header
        header_frame = ctk.CTkFrame(self.smart_mode_tab)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text="🧠 Smart Mode - ML-Powered Recommendations",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=15)
        
        # Smart Mode toggle
        self.smart_mode_switch = ctk.CTkSwitch(
            header_frame,
            text="Enable Smart Mode",
            variable=self.smart_mode_enabled,
            command=self.toggle_smart_mode
        )
        self.smart_mode_switch.grid(row=1, column=0, padx=15, pady=10)
        
        # Smart mode content
        self.smart_content_frame = ctk.CTkScrollableFrame(self.smart_mode_tab)
        self.smart_content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.smart_content_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize smart mode display
        self.update_smart_mode_display()
        
    def refresh_analytics(self):
        """Refresh analytics data and display"""
        try:
            # Clear existing content
            for widget in self.analytics_content_frame.winfo_children():
                widget.destroy()
                
            # Get analytics data
            insights = self.transformer.get_ml_insights()
            dashboard_data = self.analytics.get_dashboard_summary()
            
            if not insights:
                ctk.CTkLabel(
                    self.analytics_content_frame,
                    text="🔍 No learning data available yet.\nStart transforming passwords to see analytics!",
                    font=ctk.CTkFont(size=14)
                ).grid(row=0, column=0, pady=50)
                return
                
            # Overview section
            self.create_overview_section(dashboard_data)
            
            # Learning insights section  
            self.create_learning_insights_section(insights)
            
            # Pattern effectiveness section
            self.create_pattern_effectiveness_section(insights)
            
        except Exception as e:
            ctk.CTkLabel(
                self.analytics_content_frame,
                text=f"Error loading analytics: {str(e)}",
                text_color="red"
            ).grid(row=0, column=0, pady=20)
            
    def create_overview_section(self, data):
        """Create overview section in analytics"""
        overview_frame = ctk.CTkFrame(self.analytics_content_frame)
        overview_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        overview_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        ctk.CTkLabel(
            overview_frame,
            text="📋 Overview",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=3, pady=10)
        
        # Stats cards
        overview = data.get('overview', {})
        
        # Total transformations
        total_frame = ctk.CTkFrame(overview_frame)
        total_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(total_frame, text="Total Transformations", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        ctk.CTkLabel(total_frame, text=str(overview.get('total_transformations', 0)), 
                    font=ctk.CTkFont(size=20)).pack()
        
        # Success rate
        success_frame = ctk.CTkFrame(overview_frame)
        success_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(success_frame, text="Success Rate", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        ctk.CTkLabel(success_frame, text=f"{overview.get('success_rate', 0):.1%}", 
                    font=ctk.CTkFont(size=20)).pack()
        
        # Avg improvement
        improvement_frame = ctk.CTkFrame(overview_frame)
        improvement_frame.grid(row=1, column=2, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(improvement_frame, text="Avg Improvement", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        ctk.CTkLabel(improvement_frame, text=f"{overview.get('avg_improvement', 0):.1f}", 
                    font=ctk.CTkFont(size=20)).pack()
                    
    def create_learning_insights_section(self, insights):
        """Create learning insights section"""
        learning_frame = ctk.CTkFrame(self.analytics_content_frame)
        learning_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(
            learning_frame,
            text="🧠 Learning Status",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, pady=10, padx=15, sticky="w")
        
        # Learning details
        details_text = f"""
        • Patterns learned: {insights.get('patterns_learned', 0)}
        • Model trained: {'Yes' if insights.get('cluster_model_trained', False) else 'No'}
        • Average strength improvement: {insights.get('average_strength_improvement', 0):.1f}
        • Learning quality: {insights.get('average_success_rate', 0):.1%} success rate
        """
        
        ctk.CTkLabel(
            learning_frame,
            text=details_text,
            justify="left",
            font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, pady=10, padx=15, sticky="w")
        
    def create_pattern_effectiveness_section(self, insights):
        """Create pattern effectiveness section"""
        pattern_frame = ctk.CTkFrame(self.analytics_content_frame)
        pattern_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(
            pattern_frame,
            text="🎯 Pattern Effectiveness",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, pady=10, padx=15, sticky="w")
        
        # Pattern success rates
        success_rates = insights.get('success_rates_by_pattern', {})
        if success_rates:
            for i, (pattern, rate) in enumerate(success_rates.items()):
                if not pattern.endswith('_light') and not pattern.endswith('_moderate') and not pattern.endswith('_aggressive'):
                    pattern_label = ctk.CTkLabel(
                        pattern_frame,
                        text=f"{pattern.replace('_', ' ').title()}: {rate:.1%}",
                        font=ctk.CTkFont(size=12)
                    )
                    pattern_label.grid(row=i+1, column=0, pady=2, padx=15, sticky="w")
        else:
            ctk.CTkLabel(
                pattern_frame,
                text="No pattern data available yet",
                font=ctk.CTkFont(size=12)
            ).grid(row=1, column=0, pady=10, padx=15, sticky="w")
            
    def update_smart_mode_display(self):
        """Update smart mode display"""
        try:
            # Clear existing content
            for widget in self.smart_content_frame.winfo_children():
                widget.destroy()
                
            if not self.smart_mode_enabled.get():
                ctk.CTkLabel(
                    self.smart_content_frame,
                    text="🔧 Enable Smart Mode to get AI-powered recommendations\n\nSmart Mode uses machine learning to:\n• Analyze your password patterns\n• Provide personalized recommendations\n• Learn from your preferences\n• Optimize transformation strategies",
                    font=ctk.CTkFont(size=14),
                    justify="left"
                ).grid(row=0, column=0, pady=50)
                return
                
            # Smart mode is enabled - show recommendations interface
            ctk.CTkLabel(
                self.smart_content_frame,
                text="🧠 Smart Mode Active",
                font=ctk.CTkFont(size=16, weight="bold")
            ).grid(row=0, column=0, pady=10)
            
            # Test password input for recommendations
            test_frame = ctk.CTkFrame(self.smart_content_frame)
            test_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
            test_frame.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(test_frame, text="Test Password:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
            
            self.test_password_entry = ctk.CTkEntry(
                test_frame,
                placeholder_text="Enter a password to get AI recommendations...",
                height=35
            )
            self.test_password_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
            
            self.get_recommendations_button = ctk.CTkButton(
                test_frame,
                text="🔍 Analyze",
                command=self.get_smart_recommendations,
                width=100
            )
            self.get_recommendations_button.grid(row=0, column=2, padx=10, pady=10)
            
            # Recommendations display area
            self.recommendations_frame = ctk.CTkFrame(self.smart_content_frame)
            self.recommendations_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
            
        except Exception as e:
            ctk.CTkLabel(
                self.smart_content_frame,
                text=f"Error in smart mode: {str(e)}",
                text_color="red"
            ).grid(row=0, column=0, pady=20)
            
    def toggle_smart_mode(self):
        """Toggle smart mode on/off"""
        self.update_smart_mode_display()
        
    def get_smart_recommendations(self):
        """Get and display smart recommendations for test password"""
        try:
            test_password = self.test_password_entry.get()
            if not test_password:
                return
                
            # Clear previous recommendations
            for widget in self.recommendations_frame.winfo_children():
                widget.destroy()
                
            # Analyze password
            analysis = self.analyzer.analyze_password(test_password)
            
            # Get smart recommendations
            recommendations = self.transformer.get_smart_recommendations(
                test_password, analysis, "user@example.com"
            )
            
            if not recommendations:
                ctk.CTkLabel(
                    self.recommendations_frame,
                    text="No recommendations available",
                    text_color="orange"
                ).pack(pady=10)
                return
                
            # Display analysis
            analysis_text = f"""
            Password Analysis:
            • Strength: {analysis['strength_level'].replace('_', ' ').title()}
            • Pattern: {analysis['pattern_type'].replace('_', ' ').title()}
            • Score: {analysis['strength_score']}/100
            """
            
            ctk.CTkLabel(
                self.recommendations_frame,
                text=analysis_text,
                justify="left",
                font=ctk.CTkFont(size=11)
            ).pack(pady=5, padx=10, anchor="w")
            
            # Display recommendations
            rec_text = f"""
            AI Recommendations:
            • Recommended intensity: {recommendations['intensity'].title()}
            • Confidence: {recommendations['confidence']:.1%}
            • Predicted improvement: +{recommendations['effectiveness_prediction']['predicted_improvement']:.1f} points
            • Success probability: {recommendations['effectiveness_prediction']['success_probability']:.1%}
            """
            
            ctk.CTkLabel(
                self.recommendations_frame,
                text=rec_text,
                justify="left",
                font=ctk.CTkFont(size=11),
                text_color="lightgreen"
            ).pack(pady=5, padx=10, anchor="w")
            
            # Display reasoning
            reasoning = "\\n".join([f"• {reason}" for reason in recommendations.get('reasoning', [])])
            if reasoning:
                ctk.CTkLabel(
                    self.recommendations_frame,
                    text=f"Reasoning:\\n{reasoning}",
                    justify="left",
                    font=ctk.CTkFont(size=10),
                    text_color="lightblue"
                ).pack(pady=5, padx=10, anchor="w")
                
        except Exception as e:
            ctk.CTkLabel(
                self.recommendations_frame,
                text=f"Error getting recommendations: {str(e)}",
                text_color="red"
            ).pack(pady=10)
        
    def run(self):
        """Start the application"""
        self.root.mainloop()
