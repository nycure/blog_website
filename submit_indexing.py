import os
import sys
import json
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURATION ---
SITE_URL = "https://analyticsdrive.tech"
INDEXNOW_KEY = "decd7afbea4543c78251f2c1a29d33c9"
INDEXNOW_KEY_LOCATION = f"{SITE_URL}/{INDEXNOW_KEY}.txt"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"

# Google Indexing Config
GOOGLE_KEY_FILE = 'round-water-471721-n2-32e11119117b.json'
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/indexing"]

def submit_to_google(url):
    """Submits a URL to the Google Indexing API."""
    print(f"\n[Google] Submitting {url}...")
    
    if not os.path.exists(GOOGLE_KEY_FILE):
        print(f"   ❌ Error: Google key file '{GOOGLE_KEY_FILE}' not found.")
        return False

    try:
        creds = service_account.Credentials.from_service_account_file(
            GOOGLE_KEY_FILE, scopes=GOOGLE_SCOPES
        )
        service = build("indexing", "v3", credentials=creds)
        
        content = {
            "url": url,
            "type": "URL_UPDATED"
        }
        
        request = service.urlNotifications().publish(body=content)
        response = request.execute()
        
        print(f"   ✅ Success! Notification sent.")
        # print(f"   Response: {json.dumps(response, indent=2)}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error submitting to Google: {e}")
        return False

def submit_to_indexnow(url):
    """Submits a URL to the IndexNow API (Bing, Yandex, etc.)."""
    print(f"\n[IndexNow] Submitting {url}...")
    
    target_host = url.split("://")[-1].split("/")[0] # extract www.example.com
    
    data = {
        "host": target_host,
        "key": INDEXNOW_KEY,
        "keyLocation": INDEXNOW_KEY_LOCATION,
        "urlList": [url]
    }
    
    try:
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = requests.post(INDEXNOW_ENDPOINT, json=data, headers=headers)
        
        if response.status_code == 200:
            print(f"   ✅ Success! URL submitted to IndexNow.")
        elif response.status_code == 202:
             print(f"   ✅ Success! URL submitted to IndexNow (Accepted).")
        else:
            print(f"   ❌ Failed. Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
        return True

    except Exception as e:
        print(f"   ❌ Error submitting to IndexNow: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python submit_indexing.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    
    print(f"🚀 Starting Indexing Submission for: {url}")
    print("--------------------------------------------------")
    
    google_success = submit_to_google(url)
    indexnow_success = submit_to_indexnow(url)
    
    print("\n--------------------------------------------------")
    if google_success and indexnow_success:
        print("🎉 All submissions completed successfully!")
    elif google_success or indexnow_success:
        print("⚠️  Partial success. Check logs above.")
    else:
        print("❌ All submissions failed.")

if __name__ == "__main__":
    main()
