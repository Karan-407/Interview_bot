import pyttsx3

def text_to_speech_offline(text, rate=150, volume=0.9):
    """Convert text to speech offline using pyttsx3"""
    
    # Initialize the TTS engine
    engine = pyttsx3.init('nsss') 
    
    # Set properties
    engine.setProperty('rate', rate)  # Speed of speech
    engine.setProperty('volume', volume)  # Volume level (0.0 to 1.0)
    
    # Get available voices
    voices = engine.getProperty('voices')
    
    # Set voice (0 for male, 1 for female on most systems)
    if len(voices) > 1:
        engine.setProperty('voice', voices[14].id)  # Female voice
    
    # Convert text to speech
    engine.say(text)
    engine.runAndWait()

# Example usage
if __name__ == "__main__":
    text = "Hello! This is a text to speech conversion using Python."
    text_to_speech_offline(text)
