import win32com.client
import pythoncom
import time

print("Initializing COM...")
pythoncom.CoInitialize()

print("Creating SAPI voice object...")
speaker = win32com.client.Dispatch("SAPI.SpVoice")

print("Getting voices...")
voices = speaker.GetVoices()
print(f"Found {voices.Count} voices")

if voices.Count > 0:
    print("Setting voice...")
    speaker.Voice = voices.Item(0)
    print("Setting rate...")
    speaker.Rate = 1
    print("Setting volume...")
    speaker.Volume = 100

    print("Testing speech...")
    speaker.Speak("Hello, this is a test.")
    print("Waiting for speech to finish...")
    time.sleep(2)
    print("Test completed.")
else:
    print("No voices found!")

print("Uninitializing COM...")
pythoncom.CoUninitialize()