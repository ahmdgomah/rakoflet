import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
from datetime import datetime, timedelta
import winsound  # For Windows sound notifications
import sys

class ProphetPrayerReminder:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.load_settings()
        self.setup_reminder_data()
        self.create_widgets()
        self.reminder_thread = None
        self.is_running = False
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("Prophet Prayer Reminder - صلى الله عليه وسلم")
        self.root.geometry("450x600")
        self.root.resizable(False, False)
        self.root.configure(bg='#0f172a')
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap('mosque.ico')  # Optional: add mosque icon
        except:
            pass
            
    def setup_variables(self):
        """Initialize tkinter variables"""
        self.interval_var = tk.StringVar(value="30")  # Default 30 minutes
        self.sound_var = tk.BooleanVar(value=True)
        self.popup_var = tk.BooleanVar(value=True)
        self.auto_start_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Ready to start reminders")
        self.next_reminder_var = tk.StringVar(value="Not scheduled")
        self.counter_var = tk.StringVar(value="0")
        
        self.reminder_count = 0
        
    def setup_reminder_data(self):
        """Set up prayer phrases and reminders"""
        self.prayer_phrases = [
            "اللهم صل وسلم على نبينا محمد",
            "صلى الله عليه وسلم",
            "اللهم صل على محمد وعلى آل محمد",
            "عليه الصلاة والسلام",
            "اللهم صل وسلم وبارك على سيدنا محمد",
            "صلوات الله وسلامه عليه",
            "اللهم صل على النبي الأمي وسلم",
            "رسول الله صلى الله عليه وسلم"
        ]
        
        self.english_phrases = [
            "May Allah's peace and blessings be upon Prophet Muhammad",
            "Peace and blessings be upon him",
            "O Allah, send prayers upon Muhammad and his family",
            "May peace be upon the Messenger of Allah",
            "O Allah, bless our beloved Prophet Muhammad",
            "Prayers and peace of Allah be upon him",
            "May Allah honor and grant peace to His Messenger",
            "The Messenger of Allah, peace and blessings upon him"
        ]
        
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists('prayer_reminder_settings.json'):
                with open('prayer_reminder_settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.interval_var.set(settings.get('interval', '30'))
                    self.sound_var.set(settings.get('sound', True))
                    self.popup_var.set(settings.get('popup', True))
                    self.auto_start_var.set(settings.get('auto_start', False))
                    self.reminder_count = settings.get('total_count', 0)
        except Exception as e:
            print(f"Error loading settings: {e}")
            
    def save_settings(self):
        """Save settings to file"""
        try:
            settings = {
                'interval': self.interval_var.get(),
                'sound': self.sound_var.get(),
                'popup': self.popup_var.get(),
                'auto_start': self.auto_start_var.get(),
                'total_count': self.reminder_count
            }
            with open('prayer_reminder_settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def create_widgets(self):
        """Create and arrange all GUI widgets"""
        # Header
        self.create_header()
        
        # Settings frame
        self.create_settings_frame()
        
        # Control frame
        self.create_control_frame()
        
        # Status frame
        self.create_status_frame()
        
        # Prayer phrases display
        self.create_phrases_frame()
        
        # Load settings on startup
        if self.auto_start_var.get():
            self.root.after(1000, self.start_reminders)
            
    def create_header(self):
        """Create the app header"""
        header_frame = tk.Frame(self.root, bg='#0f172a', pady=20)
        header_frame.pack(fill='x')
        
        # Islamic decoration
        decoration_label = tk.Label(
            header_frame,
            text="🕌 ☪️ 🕌",
            font=('Arial', 20),
            fg='#fbbf24',
            bg='#0f172a'
        )
        decoration_label.pack()
        
        title_label = tk.Label(
            header_frame,
            text="Prophet Prayer Reminder",
            font=('Arial', 18, 'bold'),
            fg='#ffffff',
            bg='#0f172a'
        )
        title_label.pack(pady=5)
        
        arabic_title = tk.Label(
            header_frame,
            text="تذكير الصلاة على النبي",
            font=('Arial', 14),
            fg='#94a3b8',
            bg='#0f172a'
        )
        arabic_title.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="صلى الله عليه وسلم",
            font=('Arial', 16, 'bold'),
            fg='#10b981',
            bg='#0f172a'
        )
        subtitle_label.pack(pady=5)
        
    def create_settings_frame(self):
        """Create settings configuration frame"""
        settings_frame = tk.LabelFrame(
            self.root,
            text="⚙️ Settings",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#1e293b',
            bd=2,
            relief='ridge'
        )
        settings_frame.pack(padx=20, pady=10, fill='x')
        
        # Interval setting
        interval_frame = tk.Frame(settings_frame, bg='#1e293b')
        interval_frame.pack(fill='x', padx=15, pady=10)
        
        tk.Label(
            interval_frame,
            text="Reminder Interval:",
            font=('Arial', 11, 'bold'),
            fg='#ffffff',
            bg='#1e293b'
        ).pack(side='left')
        
        interval_combo = ttk.Combobox(
            interval_frame,
            textvariable=self.interval_var,
            values=['15', '30', '45', '60'],
            font=('Arial', 10),
            state='readonly',
            width=10
        )
        interval_combo.pack(side='right')
        interval_combo.bind('<<ComboboxSelected>>', self.on_settings_change)
        
        tk.Label(
            interval_frame,
            text="minutes",
            font=('Arial', 10),
            fg='#94a3b8',
            bg='#1e293b'
        ).pack(side='right', padx=5)
        
        # Notification options
        options_frame = tk.Frame(settings_frame, bg='#1e293b')
        options_frame.pack(fill='x', padx=15, pady=5)
        
        sound_check = tk.Checkbutton(
            options_frame,
            text="🔊 Sound notification",
            variable=self.sound_var,
            font=('Arial', 10),
            fg='#ffffff',
            bg='#1e293b',
            selectcolor='#10b981',
            command=self.on_settings_change
        )
        sound_check.pack(anchor='w')
        
        popup_check = tk.Checkbutton(
            options_frame,
            text="💬 Popup notification",
            variable=self.popup_var,
            font=('Arial', 10),
            fg='#ffffff',
            bg='#1e293b',
            selectcolor='#10b981',
            command=self.on_settings_change
        )
        popup_check.pack(anchor='w')
        
        auto_start_check = tk.Checkbutton(
            options_frame,
            text="🚀 Auto-start on launch",
            variable=self.auto_start_var,
            font=('Arial', 10),
            fg='#ffffff',
            bg='#1e293b',
            selectcolor='#10b981',
            command=self.on_settings_change
        )
        auto_start_check.pack(anchor='w')
        
    def create_control_frame(self):
        """Create control buttons frame"""
        control_frame = tk.Frame(self.root, bg='#0f172a', pady=15)
        control_frame.pack(fill='x')
        
        button_frame = tk.Frame(control_frame, bg='#0f172a')
        button_frame.pack()
        
        self.start_btn = tk.Button(
            button_frame,
            text="▶️ Start Reminders",
            font=('Arial', 12, 'bold'),
            bg='#10b981',
            fg='white',
            bd=0,
            padx=20,
            pady=10,
            command=self.start_reminders,
            cursor='hand2'
        )
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹️ Stop Reminders",
            font=('Arial', 12, 'bold'),
            bg='#ef4444',
            fg='white',
            bd=0,
            padx=20,
            pady=10,
            command=self.stop_reminders,
            cursor='hand2',
            state='disabled'
        )
        self.stop_btn.pack(side='left', padx=5)
        
        test_btn = tk.Button(
            button_frame,
            text="🔔 Test Notification",
            font=('Arial', 10),
            bg='#6366f1',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            command=self.test_notification,
            cursor='hand2'
        )
        test_btn.pack(side='left', padx=5)
        
    def create_status_frame(self):
        """Create status display frame"""
        status_frame = tk.LabelFrame(
            self.root,
            text="📊 Status",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#1e293b',
            bd=2,
            relief='ridge'
        )
        status_frame.pack(padx=20, pady=10, fill='x')
        
        # Current status
        status_info = tk.Frame(status_frame, bg='#1e293b')
        status_info.pack(fill='x', padx=15, pady=10)
        
        tk.Label(
            status_info,
            text="Status:",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#1e293b'
        ).pack(side='left')
        
        self.status_label = tk.Label(
            status_info,
            textvariable=self.status_var,
            font=('Arial', 10),
            fg='#10b981',
            bg='#1e293b'
        )
        self.status_label.pack(side='right')
        
        # Next reminder time
        next_info = tk.Frame(status_frame, bg='#1e293b')
        next_info.pack(fill='x', padx=15, pady=5)
        
        tk.Label(
            next_info,
            text="Next reminder:",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#1e293b'
        ).pack(side='left')
        
        self.next_label = tk.Label(
            next_info,
            textvariable=self.next_reminder_var,
            font=('Arial', 10),
            fg='#fbbf24',
            bg='#1e293b'
        )
        self.next_label.pack(side='right')
        
        # Reminder counter
        counter_info = tk.Frame(status_frame, bg='#1e293b')
        counter_info.pack(fill='x', padx=15, pady=5)
        
        tk.Label(
            counter_info,
            text="Total reminders sent:",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#1e293b'
        ).pack(side='left')
        
        self.counter_label = tk.Label(
            counter_info,
            textvariable=self.counter_var,
            font=('Arial', 10, 'bold'),
            fg='#10b981',
            bg='#1e293b'
        )
        self.counter_label.pack(side='right')
        
        self.update_counter_display()
        
    def create_phrases_frame(self):
        """Create prayer phrases display frame"""
        phrases_frame = tk.LabelFrame(
            self.root,
            text="🤲 Prayer Phrases",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#1e293b',
            bd=2,
            relief='ridge'
        )
        phrases_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        # Create scrollable text widget
        text_frame = tk.Frame(phrases_frame, bg='#1e293b')
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.phrases_text = tk.Text(
            text_frame,
            font=('Arial', 11),
            bg='#334155',
            fg='#ffffff',
            bd=0,
            relief='flat',
            height=8,
            wrap='word',
            state='disabled'
        )
        
        scrollbar = tk.Scrollbar(text_frame, command=self.phrases_text.yview)
        self.phrases_text.config(yscrollcommand=scrollbar.set)
        
        self.phrases_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.populate_phrases()
        
    def populate_phrases(self):
        """Populate the phrases text widget"""
        self.phrases_text.config(state='normal')
        self.phrases_text.delete(1.0, tk.END)
        
        self.phrases_text.insert(tk.END, "Arabic Prayers:\n", 'header')
        for i, phrase in enumerate(self.prayer_phrases, 1):
            self.phrases_text.insert(tk.END, f"{i}. {phrase}\n", 'arabic')
            
        self.phrases_text.insert(tk.END, "\nEnglish Translations:\n", 'header')
        for i, phrase in enumerate(self.english_phrases, 1):
            self.phrases_text.insert(tk.END, f"{i}. {phrase}\n", 'english')
            
        # Configure text tags
        self.phrases_text.tag_configure('header', foreground='#fbbf24', font=('Arial', 12, 'bold'))
        self.phrases_text.tag_configure('arabic', foreground='#10b981', font=('Arial', 12))
        self.phrases_text.tag_configure('english', foreground='#94a3b8', font=('Arial', 10))
        
        self.phrases_text.config(state='disabled')
        
    def start_reminders(self):
        """Start the reminder system"""
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.status_var.set("Reminders active")
            
            # Start reminder thread
            self.reminder_thread = threading.Thread(target=self.reminder_loop, daemon=True)
            self.reminder_thread.start()
            
            # Update next reminder time
            self.update_next_reminder_time()
            
    def stop_reminders(self):
        """Stop the reminder system"""
        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_var.set("Reminders stopped")
        self.next_reminder_var.set("Not scheduled")
        
    def reminder_loop(self):
        """Main reminder loop running in separate thread"""
        while self.is_running:
            interval_minutes = int(self.interval_var.get())
            interval_seconds = interval_minutes * 60
            
            # Wait for the specified interval
            for _ in range(interval_seconds):
                if not self.is_running:
                    return
                time.sleep(1)
                
            # Send reminder if still running
            if self.is_running:
                self.send_reminder()
                self.update_next_reminder_time()
                
    def send_reminder(self):
        """Send a prayer reminder notification"""
        import random
        
        # Select random phrases
        arabic_phrase = random.choice(self.prayer_phrases)
        english_phrase = random.choice(self.english_phrases)
        
        # Play sound if enabled
        if self.sound_var.get():
            try:
                # Windows sound
                if sys.platform == "win32":
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                else:
                    # For other systems, you might want to use a different approach
                    print("\a")  # Terminal bell
            except:
                pass
                
        # Show popup if enabled
        if self.popup_var.get():
            self.root.after(0, lambda: self.show_reminder_popup(arabic_phrase, english_phrase))
            
        # Update counter
        self.reminder_count += 1
        self.root.after(0, self.update_counter_display)
        self.save_settings()
        
    def show_reminder_popup(self, arabic_phrase, english_phrase):
        """Show reminder popup window"""
        popup = tk.Toplevel(self.root)
        popup.title("Prayer Reminder")
        popup.geometry("400x300")
        popup.configure(bg='#0f172a')
        popup.resizable(False, False)
        
        # Center the popup
        popup.transient(self.root)
        popup.grab_set()
        
        # Content frame
        content_frame = tk.Frame(popup, bg='#0f172a', pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Header
        tk.Label(
            content_frame,
            text="🕌 Time for Prayer 🕌",
            font=('Arial', 16, 'bold'),
            fg='#fbbf24',
            bg='#0f172a'
        ).pack(pady=10)
        
        # Arabic phrase
        tk.Label(
            content_frame,
            text=arabic_phrase,
            font=('Arial', 14, 'bold'),
            fg='#10b981',
            bg='#0f172a',
            wraplength=350
        ).pack(pady=10)
        
        # English translation
        tk.Label(
            content_frame,
            text=english_phrase,
            font=('Arial', 11),
            fg='#94a3b8',
            bg='#0f172a',
            wraplength=350
        ).pack(pady=10)
        
        # Close button
        tk.Button(
            content_frame,
            text="Ameen - Close",
            font=('Arial', 12, 'bold'),
            bg='#10b981',
            fg='white',
            bd=0,
            padx=20,
            pady=8,
            command=popup.destroy,
            cursor='hand2'
        ).pack(pady=20)
        
        # Auto-close after 10 seconds
        popup.after(10000, popup.destroy)
        
    def test_notification(self):
        """Test the notification system"""
        self.send_reminder()
        
    def update_next_reminder_time(self):
        """Update the next reminder time display"""
        if self.is_running:
            interval_minutes = int(self.interval_var.get())
            next_time = datetime.now() + timedelta(minutes=interval_minutes)
            self.next_reminder_var.set(next_time.strftime("%H:%M:%S"))
            
    def update_counter_display(self):
        """Update the reminder counter display"""
        self.counter_var.set(str(self.reminder_count))
        
    def on_settings_change(self, event=None):
        """Handle settings changes"""
        self.save_settings()
        if self.is_running:
            self.update_next_reminder_time()
            
    def on_closing(self):
        """Handle application closing"""
        self.stop_reminders()
        self.save_settings()
        self.root.destroy()

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = ProphetPrayerReminder(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
