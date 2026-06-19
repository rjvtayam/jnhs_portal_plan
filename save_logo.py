"""
Save the JNHS logo to the assets folder.
Run this script after pasting the base64 data below.

Usage:
  1. Right-click the logo image in the chat → Copy
  2. Open https://base64.guru/converter/encode/image
  3. Upload the logo PNG → Copy the base64 string
  4. Paste it in the LOGO_BASE64 variable below
  5. Run: python save_logo.py
"""
import base64, os

# Paste your base64 string here (without the data:image/png;base64, prefix)
LOGO_BASE64 = ""

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "frontend", "assets", "images")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "logo.png")

if not LOGO_BASE64:
    print("ERROR: Paste your base64 string in LOGO_BASE64 variable first!")
    print("Steps:")
    print("  1. Go to https://base64.guru/converter/encode/image")
    print("  2. Upload the JNHS logo PNG")
    print("  3. Copy the base64 output")
    print("  4. Paste it in save_logo.py → LOGO_BASE64")
    print("  5. Run: python save_logo.py")
else:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "wb") as f:
        f.write(base64.b64decode(LOGO_BASE64))
    print(f"Logo saved to: {OUTPUT_FILE}")
