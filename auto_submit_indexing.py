import sqlite3
import xml.etree.ElementTree as ET
import datetime
import os
import submit_indexing  # Importing the existing submission logic

# --- CONFIGURATION ---
DB_FILE = "indexing.db"
SITEMAP_FILE = "output/sitemap.xml"
DAILY_LIMIT = 199

def init_db():
    """Initializes the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            url TEXT PRIMARY KEY,
            status TEXT DEFAULT 'pending',  -- 'pending', 'submitted', 'failed'
            last_submitted_at TIMESTAMP,
            submission_count INTEGER DEFAULT 0,
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def sync_sitemap_to_db():
    """Reads sitemap.xml and adds new URLs to the database."""
    if not os.path.exists(SITEMAP_FILE):
        print(f"❌ Error: Sitemap file '{SITEMAP_FILE}' not found.")
        return

    print(f"📂 Reading sitemap: {SITEMAP_FILE}")
    try:
        tree = ET.parse(SITEMAP_FILE)
        root = tree.getroot()
        
        # XML namespace handling
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [elem.text for elem in root.findall('ns:url/ns:loc', namespace)]
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        new_count = 0
        for url in urls:
            try:
                # Insert only if it doesn't exist (IGNORE)
                cursor.execute("INSERT OR IGNORE INTO urls (url) VALUES (?)", (url,))
                if cursor.rowcount > 0:
                    new_count += 1
            except sqlite3.Error as e:
                print(f"   ⚠️ Database error for {url}: {e}")
                
        conn.commit()
        conn.close()
        print(f"   ✅ Synced {len(urls)} URLs. Found {new_count} new URLs.")
        
    except ET.ParseError as e:
        print(f"❌ Error parsing sitemap: {e}")
    except Exception as e:
        print(f"❌ Unexpected error during sync: {e}")

def get_submission_batch():
    """Retrieves a batch of pending URLs, up to the daily limit."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Select pending URLs. You might want to order by discovered_at desc for newest first?
    # User said "every time i post a new articles new article it will save that in db" 
    # and "submit the 199 url". We'll prioritize pending URLs.
    # Let's order by discovered_at DESC to prioritize newer articles if the backlog is huge.
    cursor.execute('''
        SELECT url FROM urls 
        WHERE status = 'pending' 
        ORDER BY discovered_at DESC 
        LIMIT ?
    ''', (DAILY_LIMIT,))
    
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def update_url_status(url, status):
    """Updates the status of a URL in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    timestamp = datetime.datetime.now().isoformat()
    
    if status == 'submitted':
        cursor.execute('''
            UPDATE urls 
            SET status = ?, last_submitted_at = ?, submission_count = submission_count + 1
            WHERE url = ?
        ''', (status, timestamp, url))
    else:
        # separate handling if we wanted to retry failed ones differently
        cursor.execute('''
            UPDATE urls 
            SET status = ?, last_submitted_at = ?
            WHERE url = ?
        ''', (status, timestamp, url))
        
    conn.commit()
    conn.close()

def print_stats():
    """Prints database statistics."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM urls")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM urls WHERE status='submitted'")
    submitted = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM urls WHERE status='pending'")
    pending = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n--------------------------------------------------")
    print(f"📊 Indexing Stats:")
    print(f"   Total URLs: {total}")
    print(f"   Submitted:  {submitted}")
    print(f"   Pending:    {pending}")
    print("--------------------------------------------------\n")

def main():
    print("🚀 Starting Automatic Indexing Workflow...")
    
    # 1. Initialize DB
    init_db()
    
    # 2. Sync Sitemap
    sync_sitemap_to_db()
    
    # 3. Get Batch
    batch = get_submission_batch()
    
    if not batch:
        print("🎉 No pending URLs to submit!")
        print_stats()
        return

    print(f"\nProcessing batch of {len(batch)} URLs (Limit: {DAILY_LIMIT})...")
    
    # 4. Process Batch
    count = 0
    for url in batch:
        count += 1
        print(f"\n[{count}/{len(batch)}] Processing: {url}")
        
        # Call existing submission logic
        # Note: submit_indexing.py prints its own output, so we'll see that.
        
        # We assume if the function returns True, it was successful.
        # However, submit_indexing.py functions return True/False.
        
        g_success = submit_indexing.submit_to_google(url)
        i_success = submit_indexing.submit_to_indexnow(url)
        
        if g_success or i_success:
             # If at least one succeeded, we mark as submitted. 
             # Ideally both should success, but we don't want to get stuck on partial failures forever.
             # You could refine this to 'partial' status if needed.
             update_url_status(url, 'submitted')
        else:
             print(f"   ❌ Failed to submit to both services.")
             # Optionally update to 'failed' or leave as 'pending' to retry next time.
             # Let's leave as pending or maybe 'failed' if we want to exclude them from the immediate next batch?
             # For now, let's leave them as pending but maybe we should have a retry count check later.
             # To avoid infinite loops on bad URLs, we could set to 'failed'.
             update_url_status(url, 'failed')

    print_stats()
    print("✅ Batch processing complete.")

if __name__ == "__main__":
    main()
