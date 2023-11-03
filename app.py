from flask import Flask, render_template, request, jsonify
from main import find_best_resume
import fitz
import re

app = Flask(__name__)

def load_resume(resumes):
    text_data = []
    resume_names = []
    for file in resumes:
        resume_names.append(file.filename)
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in pdf:
            text += str(page.get_text())
        text_data.append(text.replace("   ",""))
    return text_data , resume_names

def load_job(job_dec):
    job_description = job_dec.read().decode('utf-8')
    return re.sub(r'\s+', ' ', job_description).strip()
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rank', methods=['POST'])
def rank_resumes():
    job_description_raw = request.files['jobDescription']
    resumes_data = [request.files[key] for key in request.files if key.startswith('resume_')]
    
    # Process the files and rank the resumes
    best_resume = find_best_resume(load_resume(resumes_data),load_job(job_description_raw))
    print("Successfully sort Resums")
    return jsonify(best_resume)


if __name__ == '__main__':
    app.run(debug=True)

