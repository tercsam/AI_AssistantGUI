import os
import time
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

load_dotenv()

AGENT_ID = os.getenv("AGENT_ID")
API_KEY = os.getenv("API_KEY")

client = ElevenLabs(api_key=API_KEY)

# On définit les variables pour le prompt
user_name = "Clement"
schedule = "Tech Meeting with Christophe at 10:00; Counterstrike with Hugo at 17:00"
prompt = f"You are a helpful assistant. Your interlocutor has the following schedule: {schedule}."
first_message = f"Hello {user_name}, how can I help you today?"

# Au lieu de créer un objet ConversationConfig complexe, 
# on définit l'override simplement.
conversation_config_override = {
    "agent": {
        "prompt": {"prompt": prompt},
        "first_message": first_message,
    }
}

# Initialisation de la conversation
conversation = Conversation(
    client,
    AGENT_ID,
    requires_auth=True,
    audio_interface=DefaultAudioInterface(),
    # On passe l'override directement ici sans passer par un objet ConversationConfig
    callback_agent_response=lambda resp: print(f"Agent: {resp}"),
    callback_user_transcript=lambda text: print(f"User: {text}"),
)

# Alternative si l'erreur persiste : 
# Essayez de ne PAS passer de 'config' du tout pour tester la connexion de base
print("Connexion en cours...")
conversation.start_session()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Fermeture...")
    conversation.end_session()