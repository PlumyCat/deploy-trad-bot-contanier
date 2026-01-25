"""
Documentation Server - Flask application for serving Power Platform Guide

This server provides a web interface for the complete Power Platform deployment guide.

Features:
- Route /procedure: Serves the Power Platform guide with auto-generated TOC
- Route /health: Health check endpoint for monitoring
- Markdown to HTML conversion with syntax highlighting
- Automatic table of contents generation from headers
- Clean, responsive design with navigation
- Image serving from /images/ directory

Author: Aux Petits Oignons Team
Version: 1.1.0
Story: STORY-011 (Serveur Flask pour Documentation Power Platform)
Port: 8080 (mapped to 5545 externally via docker-compose.yml)
"""

from flask import Flask, redirect, send_from_directory, abort, jsonify
import markdown
import os
import re
from datetime import datetime, timezone

app = Flask(__name__)

# ============================================
# Helper Functions
# ============================================

def generate_toc(html_content):
    """
    Generate a table of contents from HTML headers (h1, h2, h3).

    Args:
        html_content: HTML string with headers

    Returns:
        tuple: (toc_html, content_with_ids) where content has added anchor IDs
    """
    # Find all headers (h1, h2, h3)
    header_pattern = re.compile(r'<(h[123])>(.+?)</h\1>', re.IGNORECASE)
    headers = []

    def add_id_to_header(match):
        """Add ID attribute to header for anchor linking"""
        tag = match.group(1)
        content = match.group(2)

        # Create slug from header text
        slug = re.sub(r'[^\w\s-]', '', content.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')

        # Store header for TOC
        headers.append({
            'level': int(tag[1]),
            'text': content,
            'id': slug
        })

        return f'<{tag} id="{slug}">{content}</{tag}>'

    # Add IDs to all headers
    content_with_ids = header_pattern.sub(add_id_to_header, html_content)

    # Generate TOC HTML
    toc_html = '<nav class="toc">\n<h2>📑 Table des matières</h2>\n<ul>\n'

    for header in headers:
        indent_class = f'toc-level-{header["level"]}'
        toc_html += f'  <li class="{indent_class}"><a href="#{header["id"]}">{header["text"]}</a></li>\n'

    toc_html += '</ul>\n</nav>'

    return toc_html, content_with_ids


# ============================================
# Routes
# ============================================

@app.route("/")
def index():
    """Redirect root to /procedure"""
    return redirect("/procedure")


@app.route("/health")
def health():
    """
    Health check endpoint for monitoring.

    Returns JSON with:
    - status: "healthy"
    - service: "documentation-server"
    - timestamp: ISO 8601 timestamp
    - port: 8080 (internal, mapped to 5545 externally)
    """
    return jsonify({
        "status": "healthy",
        "service": "documentation-server",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "port": 8080,
        "endpoints": {
            "/": "Redirect to /procedure",
            "/procedure": "Power Platform documentation",
            "/health": "Health check endpoint",
            "/images/<filename>": "Serve documentation images"
        }
    })


@app.route("/procedure")
def procedure():
    """
    Serve the Power Platform documentation guide.

    Reads GUIDE_POWER_PLATFORM_COMPLET.md from /app/src/, converts it to HTML,
    generates a table of contents, and returns a formatted HTML page.
    """
    doc_path = "/app/src/GUIDE_POWER_PLATFORM_COMPLET.md"

    # Check if documentation file exists
    if not os.path.exists(doc_path):
        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Documentation non disponible</title>
<style>
body{{font-family:Arial,sans-serif;max-width:800px;margin:100px auto;padding:20px;text-align:center;}}
h1{{color:#d9534f;}}
.error-box{{background:#f8d7da;border:1px solid #f5c6cb;padding:20px;border-radius:5px;}}
</style>
</head><body>
<h1>⚠️ Documentation non disponible</h1>
<div class="error-box">
<p>Le fichier <code>{doc_path}</code> est introuvable.</p>
<p>Le repository source n'a peut-être pas été cloné correctement au démarrage du container.</p>
<p><strong>Solution:</strong> Redémarrez le container pour forcer le clone du repository.</p>
</div>
</body></html>""", 404

    # Read and convert Markdown to HTML
    with open(doc_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Convert markdown to HTML with extensions
    html_content = markdown.markdown(
        md_content,
        extensions=[
            "fenced_code",
            "tables",
            "toc",
            "codehilite",
            "nl2br"
        ]
    )

    # Fix image paths: convert images/xxx.png to /images/xxx.png
    html_content = re.sub(r'"images/', r'"/images/', html_content)
    html_content = re.sub(r"'images/", r"'/images/", html_content)

    # Generate table of contents
    toc_html, content_with_ids = generate_toc(html_content)

    # Return complete HTML page with TOC and content
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Guide Power Platform Complet - Aux Petits Oignons</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}

        .container {{
            display: flex;
            max-width: 1600px;
            margin: 0 auto;
        }}

        /* Sidebar with TOC */
        .sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 300px;
            height: 100vh;
            background: #fff;
            border-right: 1px solid #ddd;
            overflow-y: auto;
            padding: 20px;
            box-shadow: 2px 0 5px rgba(0,0,0,0.05);
        }}

        .toc h2 {{
            color: #0078d4;
            font-size: 1.2em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #0078d4;
        }}

        .toc ul {{
            list-style: none;
            padding: 0;
        }}

        .toc li {{
            margin: 5px 0;
        }}

        .toc a {{
            text-decoration: none;
            color: #333;
            display: block;
            padding: 5px 10px;
            border-radius: 4px;
            transition: all 0.2s;
        }}

        .toc a:hover {{
            background: #e8f4ff;
            color: #0078d4;
        }}

        .toc-level-1 a {{
            font-weight: bold;
            padding-left: 10px;
        }}

        .toc-level-2 a {{
            padding-left: 25px;
            font-size: 0.95em;
        }}

        .toc-level-3 a {{
            padding-left: 40px;
            font-size: 0.9em;
            color: #666;
        }}

        /* Main content */
        .content {{
            margin-left: 320px;
            padding: 40px;
            background: #fff;
            min-height: 100vh;
            max-width: 1200px;
        }}

        /* Typography */
        h1, h2, h3, h4, h5, h6 {{
            color: #0078d4;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #0078d4;
        }}

        h1 {{
            font-size: 2.5em;
            margin-top: 0;
        }}

        h2 {{
            font-size: 2em;
            border-bottom: 2px solid #0078d4;
        }}

        h3 {{
            font-size: 1.5em;
            border-bottom: 1px solid #ccc;
        }}

        p {{
            margin: 15px 0;
        }}

        /* Code blocks */
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
            color: #c7254e;
        }}

        pre {{
            background: #f8f8f8;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #0078d4;
            margin: 20px 0;
        }}

        pre code {{
            background: transparent;
            padding: 0;
            color: #333;
        }}

        /* Tables */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 25px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 12px 15px;
            text-align: left;
        }}

        th {{
            background: #0078d4;
            color: white;
            font-weight: bold;
        }}

        tr:nth-child(even) {{
            background: #f9f9f9;
        }}

        tr:hover {{
            background: #f0f8ff;
        }}

        /* Images */
        img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin: 20px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: block;
        }}

        /* Blockquotes */
        blockquote {{
            border-left: 4px solid #ffa500;
            padding-left: 20px;
            margin: 20px 0;
            color: #666;
            font-style: italic;
            background: #fff8e1;
            padding: 15px 20px;
            border-radius: 0 5px 5px 0;
        }}

        /* Lists */
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}

        li {{
            margin: 8px 0;
        }}

        /* Links */
        a {{
            color: #0078d4;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        /* Smooth scroll */
        html {{
            scroll-behavior: smooth;
        }}

        /* Responsive design */
        @media (max-width: 1024px) {{
            .sidebar {{
                width: 250px;
            }}

            .content {{
                margin-left: 270px;
                padding: 30px;
            }}
        }}

        @media (max-width: 768px) {{
            .container {{
                flex-direction: column;
            }}

            .sidebar {{
                position: static;
                width: 100%;
                height: auto;
                border-right: none;
                border-bottom: 1px solid #ddd;
            }}

            .content {{
                margin-left: 0;
                padding: 20px;
            }}
        }}

        /* Checklist styling */
        .checklist {{
            list-style: none;
            padding-left: 0;
        }}

        .checklist li {{
            padding: 8px 0;
            position: relative;
            padding-left: 30px;
        }}

        .checklist li:before {{
            content: '☐';
            position: absolute;
            left: 0;
            font-size: 1.2em;
            color: #0078d4;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            {toc_html}
        </div>
        <div class="content">
            {content_with_ids}
        </div>
    </div>
</body>
</html>"""


@app.route("/images/<path:filename>")
def serve_images(filename):
    """
    Serve images from the /app/src/images/ directory.

    Args:
        filename: Path to the image file

    Returns:
        Image file or 404 if not found
    """
    images_dir = "/app/src/images"

    if os.path.exists(os.path.join(images_dir, filename)):
        return send_from_directory(images_dir, filename)

    abort(404)


@app.route("/static/<path:filename>")
def serve_static(filename):
    """
    Serve static files from /app/src/ directory.

    Args:
        filename: Path to the static file

    Returns:
        Static file or 404 if not found
    """
    return send_from_directory("/app/src", filename)


# ============================================
# Main
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Documentation Server - Aux Petits Oignons")
    print("=" * 60)
    print(f"Starting on http://0.0.0.0:8080")
    print(f"")
    print(f"Endpoints:")
    print(f"  • http://localhost:5545/procedure - Documentation complète")
    print(f"  • http://localhost:5545/health    - Health check")
    print(f"")
    print(f"Note: Port 8080 (internal) is mapped to 5545 (external)")
    print("=" * 60)

    app.run(host="0.0.0.0", port=8080, debug=False)
