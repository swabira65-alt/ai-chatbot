# 🤖 Full-Stack AI Chatbot Web Application

A modern, ChatGPT-inspired full-stack AI conversational web application built as an internship project. It features secure user authentication, persistent file-based chat histories, a responsive toggleable sidebar layout, and dynamic AI integration powered by FastAPI and the Google Gemini API.

---

## 🚀 Key Features

* **ChatGPT-Style UI:** Clean, modern dark sidebar layout with responsive mobile support, toggle controls, and "New Chat" session management.
* **Secure Authentication:** Built-in user registration and login system with credential tracking.
* **Persistent Session History:** Automatically saves and loads chat conversations per user via secure text-based local logs.
* **Dynamic AI Integration:** Powered by the `google-genai` SDK (Gemini API) for true natural language comprehension, backed by a robust smart fallback engine for seamless local testing.
* **High-Performance Backend:** Built with FastAPI, providing asynchronous routing, clean HTML/CSS/JavaScript frontend integration, and instant response times.

---

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, Pydantic, Uvicorn
* **Frontend:** HTML5, CSS3, Vanilla JavaScript (Single-file modular architecture)
* **AI Engine:** Google GenAI SDK (`google-genai` / Gemini API)
* **Version Control:** Git & GitHub

---

## 📁 Project Structure

```text
ai-chatbot/
│
├── main.py               # FastAPI backend server, HTML/CSS/JS frontend, and API routing
├── bot.py                # Core chatbot logic and fallback engines
├── users.txt             # Secure local user credentials store (Ignored by Git)
├── chat_history_*.txt    # User-specific chat logs (Ignored by Git)
├── .gitignore            # Excludes sensitive local tracking files
└── README.md             # Project documentation
