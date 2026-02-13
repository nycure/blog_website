import os
import sys
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURATION ---
KEY_FILE = 'round-water-471721-n2-32e11119117b.json'  # User specified key file name
SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

def get_service():
    """Authenticates and returns the Indexing API service."""
    if not os.path.exists(KEY_FILE):
        # Try adding .json extension if not present
        if os.path.exists(KEY_FILE + '.json'):
            key_path = KEY_FILE + '.json'
        else:
            print(f"❌ Error: Service account key file '{KEY_FILE}' (or '{KEY_FILE}.json') not found.")
            print("   Please verify the file name and location.")
            sys.exit(1)
    else:
         key_path = KEY_FILE

    try:
        creds = service_account.Credentials.from_service_account_file(
            key_path, scopes=SCOPES
        )
        service = build("indexing", "v3", credentials=creds)
        return service
    except Exception as e:
        print(f"❌ Error authenticating: {e}")
        sys.exit(1)

def index_url(url):
    """Submits a URL to the Google Indexing API."""
    service = get_service()
    
    content = {
        "url": url,
        "type": "URL_UPDATED"
    }

    try:
        # The actual API call
        request = service.urlNotifications().publish(body=content)
        response = request.execute()
        
        print(f"✅ Successfully submitted: {url}")
        print(f"   Response: {json.dumps(response, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Error submitting URL: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python index_now.py <URL>")
        print("Example: python index_now.py https://analyticsdrive.tech/my-new-post/")
        sys.exit(1)

    target_url = sys.argv[1]
    print(f"🚀 Submitting to Google Indexing API: {target_url}...")
    index_url(target_url)
