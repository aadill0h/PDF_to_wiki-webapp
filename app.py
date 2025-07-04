from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import os
import tempfile
import pymupdf4llm
import subprocess

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB file size limit

def pdf_to_wikitext(pdf_file):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = secure_filename(pdf_file.filename)
            pdf_path = os.path.join(tmpdir, filename)
            pdf_file.save(pdf_path)

            base = os.path.splitext(filename)[0]
            md_path = os.path.join(tmpdir, f"{base}.md")
            wiki_path = os.path.join(tmpdir, f"{base}_wiki.txt")

            # PDF → Markdown
            md_text = pymupdf4llm.to_markdown(pdf_path)
            with open(md_path, 'w') as f:
                f.write(md_text)

            # Markdown → Wikitext (with timeout)
            subprocess.run([
                'pandoc', '-f', 'markdown', '-t', 'mediawiki',
                '-o', wiki_path, md_path
            ], check=True, timeout=5)

            with open(wiki_path, 'r') as f:
                return f.read()
    except subprocess.TimeoutExpired:
        return "Conversion timed out. Please try again with a smaller file."
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    wiki_text = None
    if request.method == 'POST':
        pdf = request.files.get('pdf')
        if not pdf or not pdf.filename.lower().endswith('.pdf'):
            wiki_text = "Invalid file type. Only PDFs are allowed."
        else:
            wiki_text = pdf_to_wikitext(pdf)

    return render_template('index.html', wiki_text=wiki_text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

