from datetime import datetime
import os

print("🔐 --- USER AUTHENTICATION SYSTEM ---")

def authenticate_user():
    # Check if users file exists, create if not
    if not os.path.exists("users.txt"):
        open("users.txt", "w").close()

    while True:
        choice = input("Do you want to (1) Login or (2) Register? Enter 1 or 2: ").strip()
        
        if choice == "2":
            # Registration
            username = input("Choose a username: ").strip()
            password = input("Choose a password: ").strip()
            
            with open("users.txt", "r") as f:
                users = f.readlines()
                for user in users:
                    stored_user, _ = user.strip().split(",")
                    if stored_user == username:
                        print("❌ Username already exists! Try logging in.")
                        break
                else:
                    with open("users.txt", "a") as f_append:
                        f_append.write(f"{username},{password}\n")
                    print("✅ Registration successful! You can now log in.")
                    
        elif choice == "1":
            # Login
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()
            
            login_success = False
            with open("users.txt", "r") as f:
                for line in f:
                    stored_user, stored_pass = line.strip().split(",")
                    if stored_user == username and stored_pass == password:
                        login_success = True
                        break
            
            if login_success:
                print(f"🎉 Welcome back, {username}!")
                return username
            else:
                print("❌ Invalid username or password. Try again.")
        else:
            print("⚠️ Please enter either '1' or '2'.")

# Run authentication first before starting the chat
current_user = authenticate_user()

print(f"\n🤖 Chatbot: Hi {current_user}! I am your AI assistant. Type 'exit' to quit.")

history_file = open(f"chat_history_{current_user}.txt", "a", encoding="utf-8")
history_file.write(f"\n--- New Chat Session for {current_user}: {datetime.now()} ---\n")

last_intent = None

while True:
    user_input = input(f"{current_user}: ")
    user_input_lower = user_input.lower().strip()
    
    if user_input_lower == "exit":
        print("🤖 Chatbot: Goodbye! Saving your chat history...")
        history_file.write("Bot: Goodbye!\n")
        break
        
    if last_intent == "asked_how_are_you" and ("you" in user_input_lower or "creator" in user_input_lower or "developer" in user_input_lower):
        bot_response = f"I was created by {current_user}, an awesome developer learning AI chatbots!"
        last_intent = "discussed_creator"
    elif "hello" in user_input_lower or "hi" in user_input_lower:
        bot_response = f"Hello {current_user}! How can I help you today?"
        last_intent = "greeted"
    elif "how are you" in user_input_lower:
        bot_response = "I'm doing great! Are you curious about who made me?"
        last_intent = "asked_how_are_you"
    else:
        bot_response = "I heard you say that, but I don't understand that yet."
        last_intent = "unknown"
        
    print(f"🤖 Chatbot: {bot_response}")
    
    history_file.write(f"{current_user}: {user_input}\n")
    history_file.write(f"Bot: {bot_response}\n")

history_file.close()
print("🤖 Chatbot: Session complete. Your personal chat history file is saved!")