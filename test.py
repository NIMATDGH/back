import requests
import websocket
import json
import threading
import time

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000"
WEBSOCKET_URL_FORMAT = "ws://127.0.0.1:8000/ws/chat/{channel_id}/"

# --- Test User Details ---
TEST_USERNAME = "testuser_from_script"
TEST_PASSWORD = "a_very_secure_password_123"

def run_test():
    """
    Runs a full end-to-end test of the Django chat backend.
    """
    session = requests.Session()
    
    # --- PROXY FIX ---
    # Explicitly disable proxies for this session to bypass system settings.
    session.proxies = {"http": None, "https": None}
    
    access_token = None

    def print_step(message):
        print(f"\n--- STEP: {message} ---")

    def print_success(message):
        print(f"✅ SUCCESS: {message}")

    def print_failure(message, response=None):
        print(f"❌ FAILURE: {message}")
        if response:
            try:
                print(f"Response Body: {response.json()}")
            except json.JSONDecodeError:
                print(f"Response Body: {response.text}")
        exit()

    # 1. Register a new user
    print_step("Registering a new user")
    register_payload = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    try:
        response = session.post(f"{BASE_URL}/api/register/", json=register_payload)
        if response.status_code == 201:
            print_success(f"User '{TEST_USERNAME}' registered.")
        # Handle case where user already exists from a previous run
        elif response.status_code == 400 and 'username already exists' in response.text:
             print("User already exists, proceeding to login.")
        else:
            print_failure("User registration failed.", response)
    except requests.exceptions.ConnectionError as e:
        print_failure(f"Could not connect to the server at {BASE_URL}. Is it running?")


    # 2. Log in to get the JWT token
    print_step("Logging in to get auth token")
    login_payload = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    response = session.post(f"{BASE_URL}/api/token/", json=login_payload)
    if response.status_code == 200:
        access_token = response.json().get("access")
        session.headers.update({"Authorization": f"Bearer {access_token}"})
        print_success("Logged in and got access token.")
    else:
        print_failure("Login failed.", response)

    # 3. Create a new server
    print_step("Creating a new server")
    server_payload = {"name": "Test Server from Script"}
    response = session.post(f"{BASE_URL}/api/servers/", json=server_payload)
    if response.status_code == 201:
        server_id = response.json().get("id")
        print_success(f"Server created with ID: {server_id}")
    else:
        print_failure("Server creation failed.", response)

    # 4. Create a new channel in the server
    print_step(f"Creating a channel in server {server_id}")
    channel_payload = {"name": "test-channel"}
    response = session.post(f"{BASE_URL}/api/servers/{server_id}/channels/", json=channel_payload)
    if response.status_code == 201:
        channel_id = response.json().get("id")
        print_success(f"Channel created with ID: {channel_id}")
    else:
        print_failure("Channel creation failed.", response)

    # 5. Test WebSocket connection and messaging
    print_step(f"Testing WebSocket for channel {channel_id}")
    ws_url = WEBSOCKET_URL_FORMAT.format(channel_id=channel_id)
    ws_app = None
    message_received = threading.Event()

    def on_message(ws, message):
        print(f"Received WebSocket message: {message}")
        data = json.loads(message)
        if data.get("author") == TEST_USERNAME and "Hello from script!" in data.get("message"):
            print_success("Correct message was broadcast back from the server.")
            message_received.set()
        else:
            print_failure(f"Received unexpected message: {message}")
        ws.close()

    def on_error(ws, error):
        print_failure(f"WebSocket error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("WebSocket connection closed.")

    def on_open(ws):
        print("WebSocket connection opened. Sending message...")
        ws.send(json.dumps({
            "message": "Hello from script!"
        }))

    # We need to pass the auth token in a cookie for Channels to authenticate
    ws_app = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        cookie=f"access_token={access_token}" # This is a simple way to pass the token
    )

    # Run WebSocket client in a separate thread
    ws_thread = threading.Thread(target=ws_app.run_forever)
    ws_thread.daemon = True
    ws_thread.start()

    # Wait for the message to be received, with a timeout
    received = message_received.wait(timeout=10)
    if not received:
        print_failure("Did not receive WebSocket message in time.")

    # 6. Verify message was saved via REST API
    print_step("Verifying message was saved to database via API")
    time.sleep(1) # Give a moment for the DB write to complete
    response = session.get(f"{BASE_URL}/api/channels/{channel_id}/messages/")
    if response.status_code == 200:
        messages = response.json()
        if any("Hello from script!" in msg['content'] for msg in messages):
            print_success("Message confirmed in database via REST API.")
        else:
            print_failure("Message was not found in the channel history.", response)
    else:
        print_failure("Could not fetch message history.", response)

    print("\n🎉 ALL TESTS PASSED! 🎉")


if __name__ == "__main__":
    run_test()
