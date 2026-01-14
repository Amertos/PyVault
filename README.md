![PyVault Banner](https://i.imgur.com/your-image-placeholder.png)

# 🛡️ PyVault - Secure Local Password Manager

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-005571?style=for-the-badge&logo=python)
![Security](https://img.shields.io/badge/Security-AES--128-green?style=for-the-badge&logo=f-secure)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

</div>

## 📌 Overview
**PyVault** is a modern, single-file password manager built with Python. It allows you to securely store, manage, and retrieve your credentials locally without needing cloud servers. 

Designed with a **"Dark Mode"** first philosophy, it features a sleek, professional UI powered by `CustomTkinter` and robust encryption using the `Fernet` (AES) implementation from the `cryptography` library.

---

## ✨ Key Features

- **🔐 Robust Encryption**: All passwords are encrypted using **Fernet (AES-128)** before being saved to the local SQLite database.
- **🎨 Modern UI/UX**: Professional Dark Theme with a split-view layout, hover effects, and responsive design.
- **🕵️ Privacy First**: 
  - Passwords are hidden by default (toggle visibility with 👁).
  - Copy-to-clipboard functionality prevents shoulder surfing (passwords never plainly displayed in the list).
- **⚡ Smart Features**:
  - **Live Search**: Filter your accounts instantly.
  - **Auto-Generator**: Built-in 20-character strong password generator.
  - **One-Click Actions**: Copy Username, Copy Password, or Delete securely.
- **🚀 Portable**: The entire application lives in a single `pyvault.py` file (plus the database and key file it generates).

---

## 🛠️ Technology Stack

| Component | Library/Technology | Usage |
|-----------|--------------------|-------|
| **Core** | `Python 3` | Main logic |
| **GUI** | `customtkinter` | Modern, high-DPI aware interface |
| **Security** | `cryptography.fernet` | Symmetric Key Encryption |
| **Database** | `sqlite3` | Local storage (No server needed) |
| **Utilities** | `pyperclip` | Clipboard management |

---

## 🚀 Installation & Setup

### Prerequisites
Make sure you have Python installed. On Windows, you might need to use `py` instead of `python` if you haven't set up PATH aliases.

### 1. Clone or Download
Download the `pyvault.py` file to a folder of your choice.

### 2. Install Dependencies
Open your terminal/command prompt in the folder and run:
```powershell
py -m pip install customtkinter cryptography pyperclip
```

### 3. Run the App
Launch the application:
```powershell
py pyvault.py
```

> **Note**: Upon first run, the app will generate a `key.key` file. **DO NOT DELETE OR LOSE THIS FILE.** If you lose it, you will lose access to all your stored passwords forever.

---

## 📖 User Guide

### 1. Adding an Account
1.  Navigate to the **Left Sidebar**.
2.  Enter the **Website Name** (e.g., "Netflix") and **Username**.
3.  Type your own password OR click **Generate Strong Password 🎲**.
4.  Click **Save to Vault**.

### 2. Retrieving a Password
1.  Find the account in the list on the **Right Side**.
2.  Use the **Search Bar** 🔍 at the top if you have many accounts.
3.  Click the **Key Icon (🔑)**.
4.  The password is automatically decrypted and copied to your clipboard! Paste it where needed (Ctrl+V).

### 3. Managing Accounts
-   **Copy Username**: Click the **User Icon (👤)**.
-   **Delete Account**: Click the **Trash Icon (🗑)** and confirm the alert.

---

## ⚠️ Security Disclaimer
*PyVault is a simple, effective tool for local password management. While it uses industry-standard encryption (Fernet/AES), it stores the encryption key locally (`key.key`). Ensure your computer is secure and do not share your `key.key` file with anyone.*

---

<div align="center">
Made with ❤️ by <a href="https://github.com/Amertos">Amer</a>
</div>
