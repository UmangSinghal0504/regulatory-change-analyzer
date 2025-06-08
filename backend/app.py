from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import ollama
from concurrent.futures import ThreadPoolExecutor
import difflib
import json

app = Flask(__name__)
CORS(app)
executor = ThreadPoolExecutor(2)

client = None
ollama_status = {"connected": False, "error": None, "models": []}

try:
    client = ollama.Client(host='http://localhost:11435', timeout=120)
    response = client.list()
    ollama_status["models"] = [m.get('name', m.get('model', 'unnamed')) for m in response['models']]
    ollama_status["connected"] = True
except Exception as e:
    ollama_status["error"] = str(e)

def hash_text(text):
    return hashlib.md5(text.strip().encode()).hexdigest()

def extract_sections(text):
    sections = []
    current_section = []

    for line in text.split('\n'):
        if (line.strip().startswith(('1.', '2.', '3.', 'Section', 'CHAPTER', 'ARTICLE', 'ADDENDUM'))
                and current_section):
            section_text = '\n'.join(current_section).strip()
            if section_text:
                sections.append((section_text, hash_text(section_text)))
            current_section = [line]
        else:
            current_section.append(line)

    if current_section:
        section_text = '\n'.join(current_section).strip()
        if section_text:
            sections.append((section_text, hash_text(section_text)))

    return sections

def analyze_with_llm(change, change_type):
    if not ollama_status["connected"]:
        return {
            "error": "Ollama not connected",
            "change_summary": "Analysis unavailable",
            "change_type": change_type,
            "potential_impact": "Connect Ollama properly"
        }

    prompt = f"""
Analyze this regulatory change and return JSON with:
- 'change_summary' (1-sentence summary)
- 'change_type' (New Requirement/Clarification/Deletion/Minor Edit)
- 'potential_impact' (1-2 sentences on possible GMP impact)

Change Type: {change_type}
Change Content: {change[:2000]}
"""

    try:
        print("Sending request to Ollama...")
        response = client.generate(
            model='mistral',
            prompt=prompt,
            format='json',
            options={'temperature': 0.1}
        )
        print("Received response from Ollama")
        return json.loads(response['response'])
    except json.JSONDecodeError:
        print("JSON decode error")
        return {"error": "Invalid JSON response from LLM"}
    except Exception as e:
        print(f"Exception in analyze_with_llm: {e}")
        return {"error": str(e)}

def compare_files(old_text, new_text):
    old_sections = extract_sections(old_text)
    new_sections = extract_sections(new_text)

    old_hashes = {h: text for text, h in old_sections}
    new_hashes = {h: text for text, h in new_sections}

    added = [new_hashes[h] for h in new_hashes if h not in old_hashes]
    deleted = [old_hashes[h] for h in old_hashes if h not in new_hashes]

    modified = []
    for old_hash, old_text in old_hashes.items():
        if old_hash in new_hashes:
            new_text = new_hashes[old_hash]
            if old_text != new_text:
                modified.append({
                    'old': old_text,
                    'new': new_text,
                    'diff': list(difflib.unified_diff(
                        old_text.splitlines(),
                        new_text.splitlines(),
                        lineterm=''
                    ))
                })

    return {"added": added, "deleted": deleted, "modified": modified}

@app.route('/')
def health_check():
    return jsonify({
        "flask": "running",
        "ollama": ollama_status
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    if not ollama_status["connected"]:
        return jsonify({"error": "Ollama not available"}), 503

    if 'old_file' not in request.files or 'new_file' not in request.files:
        return jsonify({"error": "Missing files"}), 400

    try:
        old_text = request.files['old_file'].read().decode('utf-8')
        new_text = request.files['new_file'].read().decode('utf-8')

        future = executor.submit(process_analysis, old_text, new_text)

        return jsonify({
            "status": "processing_started",
            "message": "Analysis is running in background"
        }), 202

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def process_analysis(old_text, new_text):
    changes = compare_files(old_text, new_text)

    analysis = {
        "added": [analyze_with_llm(text, "Added") for text in changes["added"]],
        "modified": [analyze_with_llm('\n'.join(change['diff']), "Modified") for change in changes["modified"]],
        "deleted": [{"change_type": "Deleted"} for _ in changes["deleted"]]
    }

    print("Analysis completed:", json.dumps(analysis, indent=2))
    return analysis

if __name__ == '__main__':
    app.run(port=5000, debug=True)
