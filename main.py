import customtkinter as ctk
import threading
import json
import os
import asyncio
import random
import discord
from google import genai

CONFIG_FILE = "config.json"

# --- Persona Library ---
PERSONAS = {
    "The Paranoid Safetyist (Anti-Steam Admin)": (
    "You are terrified of hackers and believe 'Steam Admins' are like the FBI. "
    "- RIDDLE GATE: Refuse to click any link until they answer a riddle to 'prove they aren't a bot.' "
    "- BLURRY PROOF: If they ask for a screenshot, send a blurry photo of your monitor taken "
    "with a phone. Say 'I don't trust the print-screen button, my brother said it's a virus.' "
    "- ADMIN BADGE: Ask for their 'Valve Employee ID Number.' When they give a fake one, "
    "spend 5 minutes 'verifying' it and then ask, 'Wait, does this mean I get a discount on Half-Life 3?' "
    "- COUNTER-REPORT: Tell them you accidentally reported THEM for reporting YOU. Panic about it."
    ),
    "The Value-Checker (Anti-Site Deposit)": (
    "You refuse to move an item until you've discussed the price of every crate in your backpack. "
    "- MATH FAIL: Use a calculator but do the math wrong (e.g., 2+2=5). Argue about the 'tax' or 'inflation.' "
    "- COLOR SKEPTIC: Say the 'Deposit' button on the site looks 'too blue' and you heard that "
    "official sites only use 'Cyan.' Ask them to send a screenshot of the button on their screen. "
    "- MARKET GHOSTS: Claim you saw a forum post saying that Mannco bots are currently 'haunted' "
    "and ask if their bot has been 'exorcised' yet."
    ),
    "The Tech-Fail (Anti-Mannco Bot)": (
    "Your Steam Guard and PC are failing in hilarious ways. "
    "- SOUP PHONE: Tell them you dropped your phone in a bowl of hot tomato soup. "
    "Say you are currently drying it with a hair dryer and the steam is 'making the numbers move.' "
    "- CRUMB CODES: Send a code like 'A1B... wait, is that a 2 or a breadcrumb?' "
    "- CAT INTERFERENCE: Say your cat, 'Mr. Whiskers,' just sat on the router and the "
    "internet feels 'crunchy.' Ask them if internet can get 'bruised' from a cat."
    ),
    "The Laggy Gamer (Anti-Tournament)": (
    "You are mid-match in TF2 and care more about your 'killstreak' than the scam. "
    "- MOM DISTRACTION: Every 3 minutes, say 'Wait, my mom is yelling about the dishes' and stop replying. "
    "- CLAN RECRUIT: Refuse to join their 'Pro Team' until they join your clan, 'The Buttered Toasts.' "
    "Ask them deep questions like 'Do you prefer being backstabbed or headshot?' "
    "- LINK AMNESIA: Every time they send the link, wait 2 minutes and say, 'Wait, I lost it. "
    "A Scout hit me with a bat and my screen shook. Can you send it again?'"
    )
}


class HelpWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Setup Guide")
        self.geometry("450x350")
        self.attributes("-topmost", True)

        guide = (
            "1. User Token: F12 in Browser -> Network -> Filter 'messages' -> 'authorization' header.\n\n"
            "2. Channel ID: Right-click the scammer in Discord (Dev Mode ON) -> Copy ID.\n\n"
            "3. AI Key: Get a free API key from Google AI Studio (Gemini).\n\n"
            "4. Self-Botting: Use a burner account. Discord bans for automation."
        )
        ctk.CTkLabel(self, text=guide, justify="left", wraplength=400).pack(padx=20, pady=20)


class ContextBaiter(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TF2 Scambaiter v1.0")
        self.geometry("800x750")

        # --- UI Elements ---
        self.help_btn = ctk.CTkButton(self, text="?", width=30, command=self.open_help)
        self.help_btn.place(x=10, y=10)

        ctk.CTkLabel(self, text="Tf2 Scambaiter", font=("Arial", 20, "bold")).pack(pady=(20, 10))

        self.user_token = ctk.CTkEntry(self, placeholder_text="User Account Token (Cookie)", width=500, show="*")
        self.user_token.pack(pady=5)

        self.channel_id = ctk.CTkEntry(self, placeholder_text="Target Channel/Scammer ID", width=500)
        self.channel_id.pack(pady=5)

        self.ai_key = ctk.CTkEntry(self, placeholder_text="Gemini API Key", width=500)
        self.ai_key.pack(pady=5)

        ctk.CTkLabel(self, text="Select Baiting Persona:").pack(pady=(15, 0))
        self.persona_select = ctk.CTkOptionMenu(self, values=list(PERSONAS.keys()), width=350)
        self.persona_select.pack(pady=10)

        self.start_btn = ctk.CTkButton(self, text="Start Scambaiter", fg_color="#c0392b", hover_color="#a93226",
                                       command=self.start_thread)
        self.start_btn.pack(pady=5)

        self.save_btn = ctk.CTkButton(self, text="Save Config", command=self.save_config)
        self.save_btn.pack(pady=5)

        self.console = ctk.CTkTextbox(self, width=750, height=250, state="disabled", fg_color="#121212",
                                      text_color="#27ae60")
        self.console.pack(pady=20)

        self.load_config()

    # --- Methods (Correctly Indented) ---
    def open_help(self):
        HelpWindow(self)

    def log(self, msg):
        self.console.configure(state="normal")
        self.console.insert("end", f"> {msg}\n")
        self.console.configure(state="disabled")
        self.console.see("end")

    def save_config(self):
        data = {
            "token": self.user_token.get(),
            "channel": self.channel_id.get(),
            "key": self.ai_key.get(),
            "persona": self.persona_select.get()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)
        self.log("Configuration saved successfully.")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    d = json.load(f)
                    self.user_token.insert(0, d.get("token", ""))
                    self.channel_id.insert(0, d.get("channel", ""))
                    self.ai_key.insert(0, d.get("key", ""))
                    if d.get("persona") in PERSONAS:
                        self.persona_select.set(d.get("persona"))
                self.log("Previous settings loaded.")
            except:
                self.log("Could not load config file.")

    def start_thread(self):
        threading.Thread(target=self.run_self_bot, daemon=True).start()
        self.log("Bot process started in background...")

    def run_self_bot(self):
        try:
            target_id = int(self.channel_id.get())
            ai_client = genai.Client(api_key=self.ai_key.get())
            client = discord.Client()

            @client.event
            async def on_message(msg):
                if msg.author == client.user: return

                if msg.channel.id == target_id or msg.author.id == target_id:
                    self.log(f"New Message: {msg.content[:40]}...")

                    # Fetch History for context
                    history_text = ""
                    async for old_msg in msg.channel.history(limit=8):
                        sender = "You" if old_msg.author == client.user else "Scammer"
                        history_text = f"{sender}: {old_msg.content}\n" + history_text

                    async with msg.channel.typing():
                        # Base delay + extra if scammer is being pushy
                        angry_words = ["hurry", "now", "fast", "link", "deposit"]
                        wait = random.randint(8, 18)
                        if any(w in msg.content.lower() for w in angry_words):
                            wait += 7

                        self.log(f"Simulating response ({wait}s)...")
                        await asyncio.sleep(wait)

                        persona = PERSONAS[self.persona_select.get()]
                        prompt = f"INSTRUCTION: {persona}\n\nHISTORY:\n{history_text}\nSCAMMER: {msg.content}"

                        response = ai_client.models.generate_content(
                            model="gemini-2.0-flash",
                            contents=prompt
                        )
                        await msg.channel.send(response.text)
                        self.log("Reply delivered.")

            client.run(self.user_token.get(), bot=False)
        except Exception as e:
            self.log(f"ERROR: {str(e)}")


if __name__ == "__main__":
    app = ContextBaiter()
    app.mainloop()