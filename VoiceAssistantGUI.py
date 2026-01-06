import os
import threading
import shutil
import customtkinter as ctk
from tkinter import filedialog # Pour ouvrir l'explorateur de fichiers
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

# --- CONFIGURATION ---
# On définit un chemin stable pour stocker le .env importé dans le dossier utilisateur
# pour que le .app ait toujours le droit d'y accéder.
SAVED_ENV_PATH = os.path.expanduser("~/.assistant_vocal_config")

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class ConfigWindow(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.title("Configuration")
        self.geometry("400x300")
        
        ctk.CTkLabel(self, text="Configuration requise", font=("Arial", 20, "bold")).pack(pady=20)
        ctk.CTkLabel(self, text="Veuillez importer votre fichier .env\ncontenant API_KEY et AGENT_ID", 
                     font=("Arial", 13)).pack(pady=10)
        
        # Bouton d'importation
        self.import_btn = ctk.CTkButton(self, text="Choisir un fichier .env", command=self.import_env)
        self.import_btn.pack(pady=30)

    def import_env(self):
        # Ouvre la fenêtre de sélection de fichier
        file_path = filedialog.askopenfilename(title="Sélectionner le fichier .env", 
                                             filetypes=[("Fichier ENV", "*.env"), ("Tous les fichiers", "*.*")])
        
        if file_path:
            try:
                # On copie le fichier sélectionné vers notre emplacement sécurisé
                shutil.copy(file_path, SAVED_ENV_PATH)
                
                # On force le chargement immédiat pour vérifier les clés
                load_dotenv(SAVED_ENV_PATH, override=True)
                
                if os.getenv("API_KEY") and os.getenv("AGENT_ID"):
                    self.destroy()
                    self.on_success()
                else:
                    ctk.CTkLabel(self, text="Erreur: Clés manquantes dans le fichier !", text_color="red").pack()
            except Exception as e:
                print(f"Erreur lors de l'import : {e}")

class VoiceAssistantGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Assistant Personnel")
        self.geometry("450x650")
        self.configure(fg_color="#F5F5F7")

        # Chargement des clés depuis le fichier sauvegardé
        load_dotenv(SAVED_ENV_PATH)
        self.AGENT_ID = os.getenv("AGENT_ID")
        self.API_KEY = os.getenv("API_KEY")
        
        self.client = ElevenLabs(api_key=self.API_KEY)
        self.conversation = None 
        self.init_ui()

    def init_ui(self):
        self.header = ctk.CTkLabel(self, text="Assistant Prêt", font=("SF Pro Display", 24, "bold"))
        self.header.pack(pady=(40, 10))
        
        self.status_indicator = ctk.CTkLabel(self, text="Connecté via .env importé", text_color="#86868B")
        self.status_indicator.pack(pady=(0, 20))

        self.chat_box = ctk.CTkTextbox(self, width=380, height=350, fg_color="white", corner_radius=15, border_width=1)
        self.chat_box.pack(padx=20, pady=10)
        self.chat_box.configure(state="disabled")

        self.btn_action = ctk.CTkButton(self, text="Démarrer la session", command=self.toggle_session, corner_radius=20, fg_color="#0071E3")
        self.btn_action.pack(pady=30)

    def update_chat(self, sender, message):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"{sender}: {message}\n\n")
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def toggle_session(self):
        if self.conversation is None:
            self.start_voice()
            self.btn_action.configure(text="Terminer la session", fg_color="#FF3B30")
        else:
            self.stop_voice()
            self.btn_action.configure(text="Démarrer la session", fg_color="#0071E3")

    def start_voice(self):
        threading.Thread(target=self._run_conversation, daemon=True).start()

    def _run_conversation(self):
        try:
            self.conversation = Conversation(
                self.client, self.AGENT_ID, requires_auth=True, 
                audio_interface=DefaultAudioInterface(),
                callback_agent_response=lambda resp: self.after(0, self.update_chat, "Assistant", resp),
                callback_user_transcript=lambda text: self.after(0, self.update_chat, "Vous", text),
            )
            self.conversation.start_session()
        except Exception as e:
            self.after(0, self.update_chat, "Système", f"Erreur: {str(e)}")

    def stop_voice(self):
        if self.conversation:
            self.conversation.end_session()
            self.conversation = None

def launch_app():
    app = VoiceAssistantGUI()
    app.mainloop()

if __name__ == "__main__":
    # Vérifie si le fichier existe déjà dans le dossier de config utilisateur
    if os.path.exists(SAVED_ENV_PATH):
        load_dotenv(SAVED_ENV_PATH)
        
    if not os.getenv("API_KEY") or not os.getenv("AGENT_ID"):
        config = ConfigWindow(launch_app)
        config.mainloop()
    else:
        launch_app()