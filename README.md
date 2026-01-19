# 🤖 Advanced Telegram Admin & Broadcast Bot

A powerful **Telegram management bot** built with **Aiogram 3** and **PostgreSQL**, designed to centrally manage **channels, groups, and supergroups**, send secure broadcasts, and monitor detailed statistics.

This project follows a **clean, scalable architecture** and is suitable for **production use**.

---

## 🚀 Features

### 👨‍💼 Admin & Super Admin System
- Role-based access control (Admin / Super Admin)
- Add / remove admins
- PIN-based security for sensitive actions
- Change and view personal PIN codes

### 📢 Advanced Broadcast System
- Send messages to:
  - 📢 All chats
  - 📺 Channels only
  - 👥 Groups only
  - 🔥 Supergroups only
  - 🎯 Manually selected chats
- **Copy** or **Forward** mode
- Supports:
  - Text
  - Photos
  - Videos
  - Documents
- Album protection (media groups are blocked safely)
- Detailed broadcast logging (success / failed)

### 🗂 Chat Management
- Automatically detects when the bot is added as **admin**
- Stores:
  - Chat ID
  - Type (channel / group / supergroup)
  - Title
  - Username
  - Invite link
  - Description
- Detects when the bot is removed from a chat
- Secure **chat deletion with PIN confirmation**
- Detect chats where the bot **cannot write**

### 📊 Statistics & Monitoring
- Total chats (by type)
- Daily / weekly / monthly broadcast stats
- Successful vs failed deliveries
- Admin activity tracking
- List of admins who sent messages today

### 👤 User Tracking
- Stores all users who start the bot
- Admin notifications on new users
- Full user list with join time

### 🛡 Security
- Environment-based configuration (`.env`)
- Sensitive actions protected by PIN
- Group message blocking middleware
- Admin-only middleware
- Centralized logging channel

---

## 🏗 Project Structure

├── bot.py
├── config.py
├── config.example
├── Procfile
├── requirements.txt
├── database
│ ├── init.py
│ ├── db.py
│ └── models.py
├── handlers
│ ├── admin_panel.py
│ ├── broadcast.py
│ ├── chat_member.py
│ ├── delete_chat.py
│ ├── echo.py
│ ├── start.py
│ ├── statistics.py
│ └── users.py
├── keyboards
│ ├── admin_kb.py
│ └── inline_kb.py
├── middlewares
│ ├── auth.py
│ └── block.py
├── utils
│ ├── broadcast.py
│ └── states.py
└── .gitignore



---

## ⚙️ Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
2️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
3️⃣ Install dependencies
pip install -r requirements.txt


▶️ Run the Bot
python bot.py
