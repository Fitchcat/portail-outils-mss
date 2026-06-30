import re
import base64
import os
import urllib.request
import mimetypes

with open('soutenance_presentation.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Inline local images
def replace_img(match):
    src = match.group(1)
    if src.startswith('http') or src.startswith('data:'):
        return match.group(0)
    
    import urllib.parse
    filepath = urllib.parse.unquote(src)
    
    if os.path.exists(filepath):
        mime_type, _ = mimetypes.guess_type(filepath)
        if not mime_type:
            mime_type = 'image/png'
        with open(filepath, 'rb') as img_file:
            encoded = base64.b64encode(img_file.read()).decode('utf-8')
            return f'src="data:{mime_type};base64,{encoded}"'
    else:
        print(f"Warning: Local image not found: {filepath}")
        return match.group(0)

html = re.sub(r'src="([^"]+\.(png|jpe?g|svg|webp))"', replace_img, html, flags=re.IGNORECASE)

# 2. Inline Tailwind JS
tailwind_url = "https://cdn.tailwindcss.com"
print("Downloading Tailwind JS...")
req = urllib.request.Request(tailwind_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    tailwind_js = response.read().decode('utf-8')

# Using str.replace to avoid regex escape errors with \d etc.
html = html.replace(
    '<script src="https://cdn.tailwindcss.com"></script>',
    f'<script>{tailwind_js}</script>'
)

# 3. Inline FontAwesome CSS
fa_css_url = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
print("Downloading FontAwesome CSS...")
req = urllib.request.Request(fa_css_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    fa_css = response.read().decode('utf-8')

def replace_font_url(match):
    font_path = match.group(1).strip("'\"")
    font_url = font_path.replace('../', 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/')
    download_url = font_url.split('?')[0].split('#')[0]
    
    print(f"Downloading font {download_url}...")
    try:
        req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as font_resp:
            font_data = font_resp.read()
            encoded = base64.b64encode(font_data).decode('utf-8')
            mime = 'font/woff2' if 'woff2' in download_url else 'font/woff' if 'woff' in download_url else 'font/ttf'
            return f"url('data:{mime};charset=utf-8;base64,{encoded}')"
    except Exception as e:
        print(f"Failed to download font {download_url}: {e}")
        return match.group(0)

fa_css = re.sub(r'url\(([^)]+)\)', replace_font_url, fa_css)

html = html.replace(
    '<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">',
    f'<style>{fa_css}</style>'
)

with open('soutenance_presentation_standalone.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done. Saved to soutenance_presentation_standalone.html")
