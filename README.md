# AI Game Companion Prototype 🤖🎮

A production-ready prototype for an **AI Companion System** in Unreal Engine.
This project uses a local LLM (Ollama) to convert natural language commands (e.g., "attack that enemy") into structured JSON commands that Unreal Engine can execute.

## 🚀 Quick Start (Daily Workflow)

👉 **[READ THIS FIRST: QUICKSTART_GUIDE.md](QUICKSTART_GUIDE.md)**
(Contains the **Start**, **Stop**, and **Restart** instructions you need every day).

---

## 📚 Documentation

Everything you need to set up Unreal Engine and test the API is in the `docs/` folder:

- **[📘 Blueprint Integration Tutorial](docs/BLUEPRINT_TUTORIAL.md)** – Step-by-step guide to connecting UE5 Blueprints.
- **[🗺️ UE Integration Map](docs/UE_INTEGRATION_MAP.md)** – Mapping API actions (`"attack"`) to UE Enums.
- **[🏗️ Architecture Guide](docs/ARCHITECTURE.md)** – How the system works under the hood.

---

## 🛠️ Setup & Installation

### 1. Prerequisites

- **Python 3.11+**
- **Ollama** ([Download](https://ollama.com))
- **Ngrok** (For remote access/firewall bypass)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the System

See [QUICKSTART_GUIDE.md](QUICKSTART_GUIDE.md) for the 3-terminal setup.

---

## 🧪 Testing

We have included a **Postman Collection** to make testing easy.

1. Go to `postman/` folder.
2. Import `companion_api_collection.json` into Postman.
3. Use `Send Command` to test the API.

---

## ⚠️ Common Issues & Fixes

### 1. Connection Failed (-1 or 403 Forbidden)

**Cause:** Firewall or Ngrok Browser Warning.
**Fix:** You **MUST** add this header to your Unreal Engine Request:

- `User-Agent`: `MyCustomApp/1.0`

### 2. URL Not Working

**Cause:** Ngrok URL changes every time you restart it.
**Fix:** Copy the new URL from the ngrok terminal and paste it into your Blueprint.

---

## 🎮 Supported Commands

| Command    | Example                         |
| :--------- | :------------------------------ |
| **Follow** | "follow me", "come here"        |
| **Stop**   | "stop following", "stay there"  |
| **Wait**   | "wait here"                     |
| **Attack** | "attack that enemy", "kill him" |
| **Defend** | "defend this point"             |
| **Assist** | "help me", "cover me"           |

---

## 📁 Project Structure

```
UE_testing/
├── docs/                      # Documentation & Tutorials
├── postman/                   # API Collections
├── config.py                  # LLM Prompts & Config
├── intent_compiler.py         # AI Logic (Text -> JSON)
├── mock_unreal.py             # Fake UE for testing
├── server.py                  # Flask API Server
├── run.py                     # CLI Runner
├── QUICKSTART_GUIDE.md        # Daily Instructions
└── README.md                  # This file
```
