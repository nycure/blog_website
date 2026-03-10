import os
import glob
from generate_post import generate_featured_image

CONTENT_DIR = "content"

def update_posts():
    md_files = glob.glob(os.path.join(CONTENT_DIR, "*.md"))
    print(f"Found {len(md_files)} posts. Checking for missing images...")

    for file_path in md_files:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        has_image = False
        title = ""
        slug = ""
        
        # Parse metadata
        header_end_index = 0
        for i, line in enumerate(lines):
            if line.strip() == "":
                header_end_index = i
                break
            if line.startswith("Image:"):
                has_image = True
            if line.startswith("Title:"):
                title = line.replace("Title:", "").strip()
            if line.startswith("Slug:"):
                slug = line.replace("Slug:", "").strip()

        if not has_image and title:
            if not slug:
                # Fallback slug if missing
                slug = os.path.basename(file_path).replace(".md", "")

            print(f"👉 Missing Image: {title} ({slug})")
            
            # Generate Image (using existing logic which uses Pollinations -> Unsplash -> Pillow)
            # The user specifically asked for "polenai" (Pollinations), which is Tier 1 in our existing function.
            image_rel_path = generate_featured_image(title, slug)
            
            if image_rel_path:
                # Insert Image metadata
                # find a good spot (after Title or Date)
                insert_idx = 1 # default after title
                for i, line in enumerate(lines[:10]):
                    if line.startswith("Slug:"):
                        insert_idx = i + 1
                        break
                    if line.startswith("Date:"):
                        insert_idx = i + 1
                
                lines.insert(insert_idx, f"Image: {image_rel_path}\n")
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                print(f"   ✅ Updated {os.path.basename(file_path)}")

if __name__ == "__main__":
    update_posts()
