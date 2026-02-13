# ⚡ AI Game Companion - Quickstart Guide

Use this guide to **Start**, **Stop**, and **Restart** your project daily.

---

## 🛑 How to Stop Everything

1.  **Python Server Window:** Click inside, press `Ctrl + C` (twice if needed).
2.  **Ngrok Window:** Click inside, press `Ctrl + C`.
3.  **Ollama:** You can leave it running (it uses no resources when idle).

---

## 🚀 How to Start (The "Daily Routine")

You need **3 Terminal Windows** open.

### Terminal 1: Ollama (The Brain)

Run this once. If it's already running, skip it.

```bash
ollama serve
```

### Terminal 2: Python Server (The Logic)

```bash
# 1. Navigate to folder
cd Path/To/UE_testing

# 2. Run Server
python server.py
```

_(Wait until you see "Server starting on http://0.0.0.0:5000")_

### Terminal 3: Ngrok (The Funnel)

```bash
# 1. Navigate to folder
cd Path/To/UE_testing

# 2. Start Tunnel (Free Version)
ngrok http 5000
```

---

## 🔗 CRITICAL: Update Unreal Engine

**Every time you restart ngrok, the URL changes!** (Unless you have a paid account).

1.  **Copy the new URL** from the Ngrok terminal.
    - Example: `https://cool-random-name.ngrok-free.dev`
2.  **Open Unreal Engine Blueprint.**
3.  **Find your `Call URL` node.**
4.  **Paste the NEW URL.**
    - End it with `/api/command`
    - Example: `https://cool-random-name.ngrok-free.dev/api/command`
5.  **Compile & Save.**

---

## 🛠️ Verification Checklist

If it's not working, check these 3 things in your Blueprint:

1.  **URL is correct:** Matches your _current_ ngrok window.
2.  **Header 1:** `Content-Type` = `application/json`
3.  **Header 2:** `User-Agent` = `MyCustomApp/1.0` (Mandatory for firewall!)

---

## 🧪 Quick Test (Without UE)

Use the **Postman Collection** provided in the `postman/` folder.

1.  Open Postman.
2.  Import `postman/companion_api_collection.json`.
3.  Update the URL in the "Send Command" tab.
4.  Hit **Send**.
5.  If you get `200 OK`, Unreal will work too.
