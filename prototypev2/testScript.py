# Test script to simulate a new session

import config
from main import generate_video_feed, finalize_session, get_detected_json

# Simulate detection process
print("Starting video feed for detection. Press 'q' to quit.")

# Display video feed and detect items
for frame in generate_video_feed():
    # To stop the test, break manually
    if input("Press Enter to continue, type 'q' to quit session: ") == 'q':
        break

# Finalize and save session data after testing
finalize_session()
print("Session finalized. Check 'final_session.json' for logged data.")

# Check if the JSON file has been cleared for a new session
session_data = get_detected_json()
print("Current session data after clearing:", session_data)
