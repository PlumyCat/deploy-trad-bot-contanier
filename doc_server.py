from flask import Flask, redirect, send_from_directory, abort
import markdown
import os
import re

app = Flask(__name__)

@app.route("/")
def index():
    return redirect("/procedure")

@app.route("/procedure")
def procedure():
    with open("/app/src/GUIDE_POWER_PLATFORM_COMPLET.md", "r", encoding="utf-8") as f:
        md_content = f.read()

    # Convert markdown to HTML
    html = markdown.markdown(md_content, extensions=["fenced_code", "tables"])

    # Fix image paths: convert images/xxx.png to /images/xxx.png
    html = re.sub(r'"images/', r'"/images/', html)

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Guide Power Platform Complet</title>
<style>
body{{font-family:Arial,sans-serif;max-width:1000px;margin:50px auto;padding:20px;line-height:1.6;}}
h1,h2,h3{{color:#0078d4;border-bottom:2px solid #0078d4;padding-bottom:10px;}}
code{{background:#f4f4f4;padding:2px 6px;border-radius:3px;font-family:monospace;}}
pre{{background:#f4f4f4;padding:15px;border-radius:5px;overflow-x:auto;border-left:4px solid #0078d4;}}
table{{border-collapse:collapse;width:100%;margin:20px 0;}}
th,td{{border:1px solid #ddd;padding:12px;text-align:left;}}
th{{background:#0078d4;color:white;}}
img{{max-width:100%;height:auto;border:1px solid #ddd;border-radius:5px;margin:20px 0;box-shadow:0 2px 8px rgba(0,0,0,0.1);}}
blockquote{{border-left:4px solid #ffa500;padding-left:20px;color:#666;font-style:italic;}}
.checklist{{list-style:none;padding-left:0;}}
.checklist li{{padding:5px 0;}}
</style>
</head><body>{html}</body></html>"""

@app.route("/images/<path:filename>")
def serve_images(filename):
    images_dir = "/app/src/images"
    if os.path.exists(os.path.join(images_dir, filename)):
        return send_from_directory(images_dir, filename)
    abort(404)

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("/app/src", filename)

if __name__ == "__main__":
    print("Documentation server starting on http://0.0.0.0:8080")
    print("Access the guide at http://localhost:5545/procedure")
    app.run(host="0.0.0.0", port=8080, debug=True)
