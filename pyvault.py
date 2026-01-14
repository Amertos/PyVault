import customtkinter as ctk
from cryptography.fernet import Fernet
import sqlite3
import pyperclip
import os
import random
import string
from tkinter import messagebox
from typing import Optional

# =============================================================================
# KONFIGURACIJA I TEMA (MODERN AESTHETICS)
# =============================================================================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Konstante za boje (Custom Palette)
COLOR_BG_MAIN = "#1a1a1a"      # Deep Matte Black
COLOR_BG_SIDE = "#212121"      # Dark Gray (Sidebar)
COLOR_CARD = "#2b2b2b"         # Card Background
COLOR_CARD_HOVER = "#333333"   # Card Hover
COLOR_ACCENT = "#3B8ED0"       # Primary Blue
COLOR_ACCENT_HOVER = "#1F538D"
COLOR_TEXT_PRIMARY = "#ffffff"
COLOR_TEXT_SECONDARY = "#a0a0a0"
COLOR_DANGER = "#CF6679"       # Red for delete

KEY_FILE = "key.key"
DB_NAME = "pyvault.db"

# =============================================================================
# ENKRIPCIJA
# =============================================================================
class EncryptionManager:
    def __init__(self):
        self.key = self._load_or_generate_key()
        self.cipher_suite = Fernet(self.key)

    def _load_or_generate_key(self):
        if not os.path.exists(KEY_FILE):
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as key_file:
                key_file.write(key)
            return key
        else:
            with open(KEY_FILE, "rb") as key_file:
                try:
                    return key_file.read()
                except Exception:
                    # Fallback ako je fajl korumpiran (u produkciji bi ovo bio drugaciji flow)
                    return Fernet.generate_key()

    def encrypt_password(self, password: str) -> str:
        if not password: return ""
        encrypted_bytes = self.cipher_suite.encrypt(password.encode())
        return encrypted_bytes.decode()

    def decrypt_password(self, encrypted_password_str: str) -> str:
        try:
            encrypted_bytes = encrypted_password_str.encode()
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception:
            return "[Error]"

# =============================================================================
# BAZA PODATAKA
# =============================================================================
class DatabaseManager:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self._create_table()

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def _create_table(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def add_password(self, website, username, encrypted_password):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO passwords (website, username, password) VALUES (?, ?, ?)",
                       (website, username, encrypted_password))
        conn.commit()
        conn.close()

    def get_all_passwords(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, website, username, password FROM passwords ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete_password(self, record_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM passwords WHERE id=?", (record_id,))
        conn.commit()
        conn.close()

# =============================================================================
# GUI COMPONENTS
# =============================================================================
class PasswordCard(ctk.CTkFrame):
    """Custom Widget za prikaz jednog naloga u listi."""
    def __init__(self, master, record_id, website, username, encrypted_password, 
                 decrypt_callback, delete_callback, **kwargs):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=8, **kwargs)

        self.record_id = record_id
        self.encrypted_password = encrypted_password
        self.decrypt_callback = decrypt_callback
        self.delete_callback = delete_callback
        
        # Grid layout za karticu
        self.grid_columnconfigure(0, weight=1) # Info
        self.grid_columnconfigure(1, weight=0) # Actions

        # --- INFO SEKCIJA ---
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=10)

        self.lbl_website = ctk.CTkLabel(
            self.info_frame, 
            text=website, 
            font=("Segoe UI", 16, "bold"), 
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        self.lbl_website.pack(fill="x")

        self.lbl_username = ctk.CTkLabel(
            self.info_frame, 
            text=username, 
            font=("Segoe UI", 13), 
            text_color=COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        self.lbl_username.pack(fill="x")

        # --- ACTIONS SEKCIJA ---
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=0, column=1, sticky="e", padx=10, pady=10)

        # Copy Username Icon Button
        self.btn_copy_user = ctk.CTkButton(
            self.actions_frame, text="👤", width=40, height=30,
            fg_color="#444444", hover_color="#555555",
            command=lambda: self.copy_to_clipboard(username, "Username")
        )
        self.btn_copy_user.pack(side="left", padx=2)

        # Copy Password Icon Button
        self.btn_copy_pass = ctk.CTkButton(
            self.actions_frame, text="🔑", width=40, height=30,
            fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER,
            command=lambda: self.decrypt_callback(self.encrypted_password)
        )
        self.btn_copy_pass.pack(side="left", padx=2)

        # Delete Icon Button
        self.btn_delete = ctk.CTkButton(
            self.actions_frame, text="🗑", width=40, height=30,
            fg_color=COLOR_DANGER, hover_color="#AA2222",
            command=lambda: self.delete_callback(self.record_id, website)
        )
        self.btn_delete.pack(side="left", padx=2)
        
        # Hover efekat
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def copy_to_clipboard(self, text, item_name):
        pyperclip.copy(text)
        # Trik da pristupimo glavnoj aplikaciji za status update
        # Ovo pretpostavlja da je master.master... niza struktura
        print(f"Copied {item_name}") 

    def on_enter(self, event):
        self.configure(fg_color=COLOR_CARD_HOVER)

    def on_leave(self, event):
        self.configure(fg_color=COLOR_CARD)


class PyVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()
        self.crypto = EncryptionManager()
        self.all_passwords = [] # Cache za search

        # Window Setup
        self.title("PyVault")
        self.geometry("1000x650")
        self.minsize(800, 500)
        self.configure(fg_color=COLOR_BG_MAIN)
        
        # Grid Layout: Sidebar (0) | Main Content (1)
        self.grid_columnconfigure(0, weight=0, minsize=280) 
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()
        self.refresh_list()

    def _build_sidebar(self):
        """Kreira levi panel za unos podataka."""
        self.sidebar = ctk.CTkFrame(self, fg_color=COLOR_BG_SIDE, corner_radius=0, width=280)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False) # Fix width

        # Logo / Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="PyVault 🛡️", 
            font=("Segoe UI", 24, "bold"), 
            text_color=COLOR_TEXT_PRIMARY
        )
        self.logo_label.pack(pady=(30, 10), padx=20, anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar,
            text="Secure Password Manager",
            font=("Segoe UI", 12),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.subtitle_label.pack(pady=(0, 30), padx=20, anchor="w")

        # --- INPUT FORMA ---
        self.form_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.form_frame.pack(fill="x", padx=20)

        # Website Input
        self.lbl_web = ctk.CTkLabel(self.form_frame, text="WEBSITE / APP", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_SECONDARY, anchor="w")
        self.lbl_web.pack(fill="x", pady=(10, 5))
        self.entry_website = ctk.CTkEntry(self.form_frame, height=35, placeholder_text="e.g. Netflix")
        self.entry_website.pack(fill="x")

        # Username Input
        self.lbl_user = ctk.CTkLabel(self.form_frame, text="USERNAME", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_SECONDARY, anchor="w")
        self.lbl_user.pack(fill="x", pady=(15, 5))
        self.entry_username = ctk.CTkEntry(self.form_frame, height=35, placeholder_text="e.g. email@domain.com")
        self.entry_username.pack(fill="x")

        # Password Input Group
        self.lbl_pass = ctk.CTkLabel(self.form_frame, text="PASSWORD", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_SECONDARY, anchor="w")
        self.lbl_pass.pack(fill="x", pady=(15, 5))
        
        self.pass_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.pass_frame.pack(fill="x")
        
        self.entry_password = ctk.CTkEntry(self.pass_frame, height=35, placeholder_text="••••••••")
        self.entry_password.pack(side="left", fill="x", expand=True)
        
        # Toggle Visibility Button (Small eye icon)
        self.is_pass_visible = False
        self.btn_toggle_pass = ctk.CTkButton(
            self.pass_frame, text="👁", width=35, height=35,
            fg_color="#333333", hover_color="#444444",
            command=self.toggle_password_visibility
        )
        self.btn_toggle_pass.pack(side="right", padx=(5, 0))

        # Generator Button
        self.btn_generate = ctk.CTkButton(
            self.form_frame, 
            text="Generate Strong Password 🎲", 
            fg_color="transparent", 
            border_width=1, 
            border_color=COLOR_TEXT_SECONDARY,
            text_color=COLOR_TEXT_SECONDARY,
            hover_color="#333333",
            height=30,
            command=self.generate_password
        )
        self.btn_generate.pack(fill="x", pady=(10, 20))

        # Add Button
        self.btn_add = ctk.CTkButton(
            self.form_frame, 
            text="Save to Vault", 
            font=("Segoe UI", 14, "bold"),
            height=45,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            command=self.add_entry
        )
        self.btn_add.pack(fill="x", pady=10)

        # Status Label
        self.status_label = ctk.CTkLabel(self.sidebar, text="", font=("Segoe UI", 12))
        self.status_label.pack(side="bottom", pady=20)

    def _build_main_area(self):
        """Kreira desnu stranu sa search barom i listom."""
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # --- SEARCH BAR ---
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.filter_list)
        
        self.search_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="🔍  Search accounts...",
            height=45,
            font=("Segoe UI", 14),
            corner_radius=25,
            fg_color="#2b2b2b",
            border_width=0,
            textvariable=self.search_var
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        # --- SCROLLABLE LIST ---
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame, 
            fg_color="transparent", 
            label_text=""
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        
    def generate_password(self):
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        pwd = ''.join(random.choice(chars) for _ in range(20))
        self.entry_password.delete(0, "end")
        self.entry_password.insert(0, pwd)
        # Ako je bila sakrivena, prikazi je na kratko da korisnik vidi
        if not self.is_pass_visible:
            self.toggle_password_visibility()

    def toggle_password_visibility(self):
        self.is_pass_visible = not self.is_pass_visible
        if self.is_pass_visible:
            self.entry_password.configure(show="")
            self.btn_toggle_pass.configure(fg_color=COLOR_ACCENT, text_color="white") # Indikator da je aktivno
        else:
            self.entry_password.configure(show="•")
            self.btn_toggle_pass.configure(fg_color="#333333", text_color="white")

    def add_entry(self):
        website = self.entry_website.get().strip()
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not website or not username or not password:
            self._show_status("⚠️ All fields are required!", COLOR_DANGER)
            return

        enc_pwd = self.crypto.encrypt_password(password)
        self.db.add_password(website, username, enc_pwd)
        
        # Clear & Refresh
        self.entry_website.delete(0, "end")
        self.entry_username.delete(0, "end")
        self.entry_password.delete(0, "end")
        self.entry_password.configure(show="•") # Reset visibility
        self.is_pass_visible = False
        self.btn_toggle_pass.configure(fg_color="#333333")
        
        self._show_status("✅ Saved successfully!", "#4CAF50")
        self.refresh_list()

    def _show_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)
        self.after(3000, lambda: self.status_label.configure(text=""))

    def refresh_list(self):
        # Obrisi sve
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.all_passwords = self.db.get_all_passwords()
        self.render_items(self.all_passwords)

    def filter_list(self, *args):
        query = self.search_var.get().lower()
        if not query:
            self.render_items(self.all_passwords)
            return

        filtered = [
            row for row in self.all_passwords 
            if query in row[1].lower() or query in row[2].lower() 
            # row[1] = website, row[2] = username
        ]
        self.render_items(filtered)

    def render_items(self, rows):
        """Crta kartice za prosledjene podatke."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not rows:
            ctk.CTkLabel(self.scroll_frame, text="No accounts found.", text_color="gray").pack(pady=20)
            return

        for row in rows:
            record_id, website, username, enc_pwd = row
            card = PasswordCard(
                self.scroll_frame,
                record_id=record_id,
                website=website,
                username=username,
                encrypted_password=enc_pwd,
                decrypt_callback=self.handle_decrypt,
                delete_callback=self.handle_delete
            )
            card.pack(fill="x", pady=5)

    def handle_decrypt(self, enc_pwd):
        decrypted = self.crypto.decrypt_password(enc_pwd)
        pyperclip.copy(decrypted)
        self._show_status("📋 Password copied!", COLOR_ACCENT)

    def handle_delete(self, record_id, website_name):
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete account for '{website_name}'?")
        if confirm:
            self.db.delete_password(record_id)
            self._show_status("🗑️ Account deleted.", COLOR_DANGER)
            self.refresh_list()

if __name__ == "__main__":
    app = PyVaultApp()
    app.mainloop()
