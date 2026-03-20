import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import urllib3
import os
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_PATH = '/data/config.json'
ICONS_DIR = '/data/icons'

def fetch_icons():
    if not os.path.exists(ICONS_DIR):
        os.makedirs(ICONS_DIR)
        print(f"📁 Created icons directory at {ICONS_DIR}")

    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    updated_count = 0

    for cat in config.get('bookmarks', []):
        for link in cat.get('links', []):
            url = link.get('url', '')
            name = link.get('name', '')

            if link.get('icon', '').startswith('icons/') or link.get('icon', '').startswith('/icons/'):
                continue

            print(f"🔍 Checking: {name} ({url})")

            domain = urlparse(url).netloc
            safe_domain = re.sub(r'[^a-zA-Z0-9]', '_', domain)

            try:
                resp = requests.get(url, headers=headers, timeout=5, verify=False)
                soup = BeautifulSoup(resp.content, 'html.parser')

                icon_link = soup.find('link', rel=lambda x: x and 'icon' in x.lower())

                if icon_link and icon_link.get('href'):
                    icon_url = urljoin(url, icon_link['href'])
                else:
                    icon_url = urljoin(url, '/favicon.ico')

                print(f"   ⬇️ Downloading: {icon_url}")

                img_resp = requests.get(icon_url, headers=headers, stream=True, timeout=5, verify=False)

                if img_resp.status_code == 200:
                    ext = '.ico'
                    content_type = img_resp.headers.get('Content-Type', '').lower()
                    if 'png' in content_type: ext = '.png'
                    elif 'svg' in content_type: ext = '.svg'
                    elif 'jpeg' in content_type or 'jpg' in content_type: ext = '.jpg'
                    elif 'gif' in content_type: ext = '.gif'

                    filename = f"{safe_domain}{ext}"
                    filepath = os.path.join(ICONS_DIR, filename)

                    with open(filepath, 'wb') as f:
                        for chunk in img_resp.iter_content(1024):
                            f.write(chunk)

                    link['icon'] = f"/icons/{filename}"
                    print(f"   ✅ Saved as {filename}")
                    updated_count += 1

                    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2)

                else:
                    print(f"   ❌ Failed to download (HTTP {img_resp.status_code})")

            except Exception as e:
                print(f"   ⚠️ Could not reach site ({type(e).__name__})")

    print(f"\n🎉 Done! Successfully downloaded and injected {updated_count} local icons.")

if __name__ == '__main__':
    fetch_icons()