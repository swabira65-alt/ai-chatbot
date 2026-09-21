from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from datetime import datetime

# Optional: Try importing real Google GenAI SDK if available
try:
    from google import genai
    # Replace with your API key or set environment variable GEMINI_API_KEY
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
    ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY != "YOUR_GEMINI_API_KEY" else None
except ImportError:
    ai_client = None

app = FastAPI(
    title="AI Chatbot Real AI Edition",
    description="Full-stack FastAPI chatbot featuring User Auth, ChatGPT UI, and Gemini AI integration.",
    version="3.5"
)

class UserCredentials(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    username: str
    message: str

if not os.path.exists("users.txt"):
    open("users.txt", "w").close()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Internship Assistant - ChatGPT Style</title>
        <style>
            :root {
                --sidebar-bg: #171717;
                --sidebar-hover: #212121;
                --main-bg: #ffffff;
                --text-main: #374151;
                --primary: #4f46e5;
                --border-color: #e5e7eb;
            }

            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f3f4f6; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }
            
            /* Auth Card */
            .auth-card { width: 380px; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); display: flex; flex-direction: column; overflow: hidden; }
            .auth-header { background: var(--primary); color: white; padding: 20px; text-align: center; font-weight: bold; font-size: 20px; }
            .auth-content { padding: 20px; display: flex; flex-direction: column; gap: 12px; }
            input { padding: 12px; border: 1px solid var(--border-color); border-radius: 6px; outline: none; font-size: 14px; }
            input:focus { border-color: var(--primary); }
            button { background: var(--primary); color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; transition: background 0.2s; }
            button:hover { background: #4338ca; }
            .secondary-btn { background: #e5e7eb; color: #374151; }
            .secondary-btn:hover { background: #d1d5db; }
            .error-msg { color: #dc2626; font-size: 13px; text-align: center; min-height: 18px; }
            .success-msg { color: #16a34a; font-size: 13px; text-align: center; min-height: 18px; }

            /* ChatGPT Layout */
            .app-container { display: flex; width: 100vw; height: 100vh; background: var(--main-bg); overflow: hidden; }
            
            /* Sidebar */
            .sidebar { width: 260px; background: var(--sidebar-bg); color: #ececf1; display: flex; flex-direction: column; transition: transform 0.3s ease; z-index: 10; }
            .sidebar.closed { transform: translateX(-260px); position: absolute; height: 100%; }
            .sidebar-top { padding: 12px; display: flex; flex-direction: column; gap: 8px; border-bottom: 1px solid #2f2f2f; }
            .new-chat-btn { background: transparent; border: 1px solid #565869; color: white; text-align: left; padding: 10px 12px; border-radius: 6px; display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer; }
            .new-chat-btn:hover { background: var(--sidebar-hover); }
            
            .sidebar-history { flex: 1; padding: 10px; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; }
            .history-title { font-size: 11px; text-transform: uppercase; color: #8e8ea0; padding: 8px 10px; font-weight: bold; }
            .history-item { padding: 10px; border-radius: 6px; font-size: 13px; color: #c5c5d2; cursor: pointer; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .history-item:hover { background: var(--sidebar-hover); }

            .sidebar-footer { padding: 12px; border-top: 1px solid #2f2f2f; display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #ececf1; }
            .logout-icon-btn { background: transparent; color: #ef4444; border: none; padding: 6px; cursor: pointer; border-radius: 4px; font-size: 12px; }
            .logout-icon-btn:hover { background: #2f2f2f; }

            /* Main Chat Area */
            .chat-main { flex: 1; display: flex; flex-direction: column; height: 100vh; background: var(--main-bg); position: relative; }
            .top-nav { height: 50px; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 0 16px; background: white; }
            .toggle-sidebar-btn { background: transparent; border: none; color: #4b5563; font-size: 18px; cursor: pointer; padding: 6px 10px; border-radius: 4px; }
            .toggle-sidebar-btn:hover { background: #f3f4f6; }
            
            .chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; scroll-behavior: smooth; }
            .message-wrapper { display: flex; width: 100%; }
            .message { max-width: 70%; padding: 12px 16px; border-radius: 12px; font-size: 14px; line-height: 1.5; word-break: break-word; }
            .user-msg { background: var(--primary); color: white; margin-left: auto; border-bottom-right-radius: 2px; }
            .bot-msg { background: #f4f4f5; color: #18181b; margin-right: auto; border-bottom-left-radius: 2px; border: 1px solid var(--border-color); }

            /* Input Area */
            .chat-input-container { padding: 16px 24px; background: white; border-top: 1px solid var(--border-color); display: flex; justify-content: center; }
            .chat-input-wrapper { max-width: 750px; width: 100%; display: flex; background: white; border: 1px solid #d1d5db; border-radius: 12px; padding: 8px 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }
            .chat-input-wrapper input { flex: 1; border: none; outline: none; font-size: 14px; padding: 4px; background: transparent; }
            .send-btn { background: var(--primary); color: white; border: none; width: 36px; height: 36px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-weight: bold; }
            .send-btn:hover { background: #4338ca; }

            .hidden { display: none !important; }
        </style>
    </head>
    <body>

        <!-- AUTH SCREEN -->
        <div class="auth-card" id="authCard">
            <div class="auth-header">🤖 AI Chatbot Studio</div>
            <div class="auth-content">
                <h3 style="margin: 0; text-align: center; color: var(--text-main);">Secure Login</h3>
                <input type="text" id="username" placeholder="Username">
                <input type="password" id="password" placeholder="Password">
                <button onclick="handleAuth('login')">Login</button>
                <button class="secondary-btn" onclick="handleAuth('register')">Register New Account</button>
                <div id="authMessage" class="error-msg"></div>
            </div>
        </div>

        <!-- CHATGPT STYLE APP LAYOUT -->
        <div class="app-container hidden" id="appContainer">
            
            <!-- Sidebar -->
            <div class="sidebar" id="sidebar">
                <div class="sidebar-top">
                    <button class="new-chat-btn" onclick="newChat()">
                        <span>➕</span> New Chat
                    </button>
                </div>
                <div class="history-title">Recent Conversations</div>
                <div class="sidebar-history" id="sidebarHistory">
                    <!-- Populated dynamically -->
                </div>
                <div class="sidebar-footer">
                    <span id="sidebarUsername" style="font-weight: bold; font-size: 13px;">User</span>
                    <button class="logout-icon-btn" onclick="logout()" title="Logout">🚪 Logout</button>
                </div>
            </div>

            <!-- Main Chat Panel -->
            <div class="chat-main">
                <div class="top-nav">
                    <button class="toggle-sidebar-btn" onclick="toggleSidebar()" title="Toggle Sidebar">☰</button>
                    <span style="font-weight: 600; font-size: 14px; color: #4b5563;">AI Internship Assistant</span>
                    <span style="width: 30px;"></span>
                </div>

                <div class="chat-box" id="chatBox">
                    <div class="message-wrapper">
                        <div class="message bot-msg">Hello! I am your AI assistant. Ask me anything to start chatting.</div>
                    </div>
                </div>

                <div class="chat-input-container">
                    <div class="chat-input-wrapper">
                        <input type="text" id="messageInput" placeholder="Message AI Assistant..." onkeypress="checkEnter(event)">
                        <button class="send-btn" onclick="sendMessage()">▲</button>
                    </div>
                </div>
            </div>

        </div>

        <script>
            let currentUsername = "";

            async function handleAuth(action) {
                const user = document.getElementById("username").value.trim();
                const pass = document.getElementById("password").value.trim();
                const msgDiv = document.getElementById("authMessage");

                msgDiv.className = "error-msg";
                msgDiv.innerText = "";

                if (!user || !pass) {
                    msgDiv.innerText = "Please fill in all fields.";
                    return;
                }

                try {
                    const response = await fetch(`/${action}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username: user, password: pass })
                    });
                    const data = await response.json();

                    if (!response.ok) {
                        msgDiv.innerText = data.detail || "Authentication failed.";
                    } else {
                        if (action === 'register') {
                            msgDiv.className = "success-msg";
                            msgDiv.innerText = "Registration successful! You can now login.";
                        } else {
                            currentUsername = user;
                            document.getElementById("sidebarUsername").innerText = currentUsername;
                            document.getElementById("authCard").classList.add("hidden");
                            document.getElementById("appContainer").classList.remove("hidden");
                            loadChatHistory();
                        }
                    }
                } catch (err) {
                    msgDiv.innerText = "Connection error to server.";
                }
            }

            function toggleSidebar() {
                const sidebar = document.getElementById("sidebar");
                sidebar.classList.toggle("closed");
            }

            function newChat() {
                const chatBox = document.getElementById("chatBox");
                chatBox.innerHTML = `
                    <div class="message-wrapper">
                        <div class="message bot-msg">Started a fresh conversation session! What's on your mind?</div>
                    </div>
                `;
            }

            async function loadChatHistory() {
                try {
                    const response = await fetch(`/history/${currentUsername}`);
                    const data = await response.json();
                    
                    const sidebarHistory = document.getElementById("sidebarHistory");
                    const chatBox = document.getElementById("chatBox");
                    
                    sidebarHistory.innerHTML = "";
                    chatBox.innerHTML = '';

                    if (data.history && data.history.length > 0) {
                        data.history.forEach(line => {
                            if (!line.trim()) return;
                            if (line.includes("Bot:")) {
                                appendMessage("Bot", line.split("Bot:")[1].trim(), "bot-msg", false);
                            } else if (line.includes(`${currentUsername}:`)) {
                                appendMessage(currentUsername, line.split(`${currentUsername}:`)[1].trim(), "user-msg", false);
                            }
                        });

                        const histDiv = document.createElement("div");
                        histDiv.className = "history-item";
                        histDiv.innerText = `💬 Active Log (${data.history.length} msgs)`;
                        sidebarHistory.appendChild(histDiv);
                    } else {
                        chatBox.innerHTML = `
                            <div class="message-wrapper">
                                <div class="message bot-msg">Hello ${currentUsername}! Ask me anything.</div>
                            </div>
                        `;
                        sidebarHistory.innerHTML = '<div style="color: #8e8ea0; font-size: 12px; padding: 10px;">No recent chats</div>';
                    }
                } catch (e) {
                    console.error("Could not load history");
                }
            }

            function logout() {
                currentUsername = "";
                document.getElementById("username").value = "";
                document.getElementById("password").value = "";
                document.getElementById("authMessage").innerText = "";
                document.getElementById("appContainer").classList.add("hidden");
                document.getElementById("authCard").classList.remove("hidden");
            }

            async function sendMessage() {
                const inputField = document.getElementById("messageInput");
                const text = inputField.value.trim();
                if (!text) return;

                appendMessage(currentUsername, text, "user-msg", true);
                inputField.value = "";

                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username: currentUsername, message: text })
                    });
                    const data = await response.json();
                    appendMessage("Bot", data.bot_response, "bot-msg", true);
                    loadChatHistory();
                } catch (error) {
                    appendMessage("Bot", "Error connecting to server.", "bot-msg", true);
                }
            }

            function appendMessage(sender, text, className, scrollToBottom = true) {
                const chatBox = document.getElementById("chatBox");
                const wrapper = document.createElement("div");
                wrapper.className = "message-wrapper";
                
                const msgDiv = document.createElement("div");
                msgDiv.className = `message ${className}`;
                msgDiv.innerText = text;
                
                wrapper.appendChild(msgDiv);
                chatBox.appendChild(wrapper);
                
                if(scrollToBottom) {
                    chatBox.scrollTop = chatBox.scrollHeight;
                }
            }

            function checkEnter(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/register")
def register_user(user: UserCredentials):
    with open("users.txt", "r") as f:
        for line in f:
            if not line.strip(): continue
            stored_user, _ = line.strip().split(",")
            if stored_user == user.username:
                raise HTTPException(status_code=400, detail="Username already exists!")
    with open("users.txt", "a") as f:
        f.write(f"{user.username},{user.password}\n")
    return {"status": "success", "message": f"User '{user.username}' registered successfully."}

@app.post("/login")
def login_user(user: UserCredentials):
    with open("users.txt", "r") as f:
        for line in f:
            if not line.strip(): continue
            stored_user, stored_pass = line.strip().split(",")
            if stored_user == user.username and stored_pass == user.password:
                return {"status": "success", "message": f"Welcome back, {user.username}!"}
    raise HTTPException(status_code=401, detail="Invalid username or password.")

@app.get("/history/{username}")
def get_chat_history(username: str):
    history_filename = f"chat_history_{username}.txt"
    if not os.path.exists(history_filename):
        return {"history": []}
    
    with open(history_filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return {"history": [line.strip() for line in lines if line.strip()]}

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    username = request.username
    user_input = request.message.strip()
    
    bot_response = ""
    
    # Use real Gemini AI if client is configured, otherwise fallback to a versatile smart engine
    if ai_client is not None:
        try:
            response = ai_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"You are a helpful, smart AI assistant for a user named {username}. Respond naturally and concisely to: {user_input}"
            )
            bot_response = response.text
        except Exception as e:
            bot_response = f"I am connected to your backend! (AI engine note: {str(e)})"
    else:
        # Smart dynamic fallback response so it handles any topic smoothly
        text_lower = user_input.lower()
        if "python" in text_lower:
            bot_response = f"Python is a powerful language, {username}! It's what powers this FastAPI backend and your entire internship project."
        elif "fastapi" in text_lower:
            bot_response = "FastAPI is a modern, high-performance web framework for building APIs with Python, featuring automatic docs and high speeds."
        elif "help" in text_lower:
            bot_response = "I'm here to help! You can ask me coding questions, discuss your internship project, or chat about anything you like."
        else:
            bot_response = f"That's a fascinating point, {username}. As your AI assistant running on your local server, I'm tracking your queries and logging them to your session history file seamlessly!"

    # Save to persistent history file per user
    history_filename = f"chat_history_{username}.txt"
    with open(history_filename, "a", encoding="utf-8") as history_file:
        history_file.write(f"[{datetime.now().strftime('%H:%M:%S')}] {username}: {request.message}\n")
        history_file.write(f"[{datetime.now().strftime('%H:%M:%S')}] Bot: {bot_response}\n")
        
    return {
        "username": username,
        "user_message": request.message,
        "bot_response": bot_response,
        "history_saved_to": history_filename
    }