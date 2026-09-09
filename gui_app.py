import tkinter as tk
from tkinter import scrolledtext, messagebox
import google.generativeai as genai
import os
import threading

# --- PHASE 3: AGENT TOOLS ---
def schedule_shoot(location: str, date: str) -> str:
    """Schedules a film shoot at a specific location and date."""
    return f"Success: Shoot scheduled at {location} on {date}."

def generate_vfx_prompt(scene_description: str) -> str:
    """Generates a detailed visual prompt for VFX engines based on a scene."""
    return f"VFX Moodboard Prompt: Cinematic lighting, 8k resolution, photorealistic, {scene_description}."

# --- MAIN APP CLASS ---
class AgenticCinemaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agentic Cinema - Production Assistant")
        self.root.geometry("500x600")
        self.root.configure(bg="#f4f4f9")

        # Set up Gemini
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        if not api_key:
            messagebox.showwarning("Missing API Key", "Please set the GOOGLE_API_KEY environment variable. You can enter it in the app!")
        
        # Optionally ask for API key if missing (simple workaround for desktop app)
        self.setup_ui()
        if not api_key:
            self.display_message("System", "Please type your Gemini API Key here and hit Send:")
            self.waiting_for_key = True
        else:
            self.init_agent(api_key)
            
    def init_agent(self, api_key):
        self.waiting_for_key = False
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[schedule_shoot, generate_vfx_prompt],
            system_instruction="You are an expert AI production assistant for a film studio. Help schedule shoots and create VFX prompts."
        )
        self.chat_session = self.model.start_chat(enable_automatic_function_calling=True)
        self.display_message("System", "Agent successfully loaded! How can I help with your production today?")

    def setup_ui(self):
        # Chat Display Area
        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Arial", 11), bg="#ffffff", fg="#333333")
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)

        # Input Frame
        input_frame = tk.Frame(self.root, bg="#f4f4f9")
        input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

        self.msg_entry = tk.Entry(input_frame, font=("Arial", 12))
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda event: self.send_message())

        send_btn = tk.Button(input_frame, text="Send", font=("Arial", 11, "bold"), bg="#0078D7", fg="white", command=self.send_message)
        send_btn.pack(side=tk.RIGHT)

    def display_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}:
{message}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def send_message(self):
        user_text = self.msg_entry.get().strip()
        if not user_text:
            return
        
        self.msg_entry.delete(0, tk.END)
        
        if getattr(self, 'waiting_for_key', False):
            self.display_message("System", "Initializing with provided key...")
            self.init_agent(user_text)
            return
            
        self.display_message("You", user_text)

        # Run AI response in a separate thread to keep UI from freezing
        threading.Thread(target=self.fetch_response, args=(user_text,)).start()

    def fetch_response(self, user_text):
        try:
            response = self.chat_session.send_message(user_text)
            self.root.after(0, self.display_message, "Assistant", response.text)
        except Exception as e:
            self.root.after(0, self.display_message, "Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = AgenticCinemaApp(root)
    root.mainloop()
