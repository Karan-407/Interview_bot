import speech_recognition as sr

def continuous_speech_recognition():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 200  # Minimum audio energy to consider for recording
    recognizer.dynamic_energy_threshold = True  # Automatically adjust energy threshold
    recognizer.pause_threshold = 3
    print("Starting continuous speech recognition. Press Ctrl+C to stop.")
    

    try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                print("Wait for 5 sec to adjust the background noise..")
                recognizer.adjust_for_ambient_noise(source, duration=5)
                print("Listening...")
                
                # Listen for audio
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=50)
                
            # Convert to text
            print(audio)
            text = recognizer.recognize_google(audio, language="en-IN")
            print(f"Recognized: {text}")
            return text
            
    except sr.WaitTimeoutError:
            # No speech detected within timeout
            return "The User did not respond"
    except sr.UnknownValueError:
            print("Could not understand audio")
            return "The User did not respond"
    except sr.RequestError as e:
            print(f"Error: {e}")
            return "The User did not respond"
    except KeyboardInterrupt:
            print("\nStopping speech recognition...")
            

if __name__ == "__main__":
    continuous_speech_recognition()
