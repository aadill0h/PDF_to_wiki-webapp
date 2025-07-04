from flask import Flask, request, render_template
import os
import pymupdf4llm
import subprocess
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def pdf_to_wikitext(pdf_path):
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    md_path = os.path.join(UPLOAD_FOLDER, f"{base_name}.md")
    wiki_path = os.path.join(UPLOAD_FOLDER, f"{base_name}_wiki.txt")

    # PDF → Markdown
    md_text = pymupdf4llm.to_markdown(pdf_path)
    with open(md_path, 'w') as f:
        f.write(md_text)

    # Markdown → Wikitext
    subprocess.run(['pandoc', '-f', 'markdown', '-t', 'mediawiki', '-o', wiki_path, md_path], check=True)

    with open(wiki_path, 'r') as f:
        wiki_content=  f.read()

    os.remove(pdf_path)
    os.remove(md_path)
    os.remove(wiki_path)

    return wiki_content

@app.route('/', methods=['GET', 'POST'])
def index():
    wiki_text = None
    if request.method == 'POST':
        pdf = request.files['pdf']
        if pdf:
            filename = f"{uuid.uuid4().hex}.pdf"
            path = os.path.join(UPLOAD_FOLDER, filename)
            pdf.save(path)

            try:
                wiki_text = pdf_to_wikitext(path)
            except Exception as e:
                wiki_text = f"Error: {e}"

    return render_template('index.html', wiki_text=wiki_text)

if __name__ == '__main__':
    app.run(debug=True)

