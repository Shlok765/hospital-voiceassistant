import win32com.client
print("Testing SAPI...")
speaker = win32com.client.Dispatch("SAPI.SpVoice")
speaker.Speak("Hello, this is a test.")
print("Test completed.")