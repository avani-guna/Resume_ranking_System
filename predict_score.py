import os
import spacy
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer , CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv
import re
import fitz
from sklearn.metrics import jaccard_score ,classification_report
from sklearn.svm import SVR
import matplotlib.pyplot as plt

nlp = spacy.load("en_core_web_lg")
# json_file_
skills = "jz_skill_patterns.jsonl"
#Adding pipe to pretrianed model
ruler = nlp.add_pipe("entity_ruler", before="ner")
# For skills extraction
ruler.from_disk(skills) 

# Step 1: Data Preprocessing using Spacy
def preprocess_resume(text):
    doc = nlp(text)
    clean_text = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
    return ' '.join(clean_text)

# Step 2: Feature Extraction
def extract_features(resumes, job_description):
    vectorizer = TfidfVectorizer()
    count_vectorizer = CountVectorizer()
    # Vectorize job description
    job_desc_tfidf = vectorizer.fit_transform([preprocess_resume(job_description)])
    job_desc_count = count_vectorizer.fit_transform([preprocess_resume(job_description)])
    # Vectorize resumes
    resume_tfidf_vecs = []
    resume_count_vecs = []
    cosine_similarities = []
    jaccard_similarities = []
    for resume in resumes:
        resume_tfidf = vectorizer.transform([preprocess_resume(resume)]).toarray()
        resume_count = count_vectorizer.transform([preprocess_resume(resume)])
        resume_tfidf_vecs.append(resume_tfidf)
        resume_count_vecs.append(resume_count)
        cosine_similarities.append(cosine_similarity(job_desc_tfidf, resume_tfidf)[0][0])
        jaccard_similarities.append((jaccard_score(job_desc_count.toarray()[0], resume_count.toarray()[0],average='weighted')))

    # # optionl 
    # jaccard_similarities = []
    # job_desc_tokens = set(preprocess_resume(job_description).split())
    # for resume in resumes:
    #     resume_tokens = set(preprocess_resume(resume).split())
    #     jaccard_similarities.append((len(job_desc_tokens.intersection(resume_tokens)) / len(job_desc_tokens.union(resume_tokens)) * 10))

    # Compute combined score
    final_scores = []
    for i in range(len(resumes)):
        final_scores.append(0.8 * cosine_similarities[i] + 0.2 * jaccard_similarities[i])

    # Get feature names
    feature_names = list(vectorizer.vocabulary_.keys())
 
    # print(resume_tfidf_vecs[0].shape)
    return resume_tfidf_vecs, final_scores


def create_svr_model(X_train, y_train, kernel='rbf', C=1.0, epsilon=0.1):
    """
    Creates and trains an SVR model with the given training data.

    Args:
        X_train (numpy.ndarray): Input data of shape (n_samples, n_features).
        y_train (numpy.ndarray): Target values of shape (n_samples,).
        kernel (str, optional): Kernel function to use. Defaults to 'rbf'.
        C (float, optional): Regularization parameter. Defaults to 1.0.
        epsilon (float, optional): Epsilon parameter. Defaults to 0.1.

    Returns:
        sklearn.svm.SVR: Trained SVR model.
    """
    X_train , y_train = np.array(X_train) , np.array(y_train)
    X_train = X_train.reshape(X_train.shape[0], -1)
    svr = SVR(kernel=kernel, C=C, epsilon=epsilon)
    svr.fit(X_train, y_train)
    yfit = svr.predict(X_train)
    # for i in range(X_train.shape[1]):
    #     plt.scatter(X_train[:,i], y_train, s=5, color="blue", label="original")
    #     plt.plot(X_train[:,i], yfit, lw=2, color="red", label="fitted")
    # plt.legend()
    # plt.show()

    return svr


## find Skill score is similar to job_description
def find_skill_score(resume_text,job_description):
    #job description data
    doc_job = nlp(preprocess_resume(job_description))
    skill_tokens = set([ent.text.lower() for ent in doc_job.ents if ent.label_ == 'SKILL'])

    # resume data
    skill_scores = []
    for text in resume_text:
        doc_resume = nlp(preprocess_resume(text))
        resume_skills = set([ent.text.lower() for ent in doc_resume.ents if ent.label_ == 'SKILL'])
        score = sum([1 for skill in resume_skills if skill in skill_tokens])
        skill_scores.append(score)

    return skill_scores

# load resume file
def load_resume(resume_folder):
    resumes = []
    resume_names = []
    for filename in os.listdir(resume_folder):
        if filename.endswith('.pdf'):
            # Open the PDF file
            with open(os.path.join(resume_folder, filename), 'rb') as f:
                # Read the PDF file
                text= ""
                with fitz.open(f) as doc:
                    for page in doc:
                        text += str(page.get_text())
                        # print(text)
                resumes.append(" ".join(text.split("\n")))
        resume_names.append(filename)
    return resumes , resume_names

# save output data
def save_output_file(ranked_resumes , output_path):
    # Write all resume scores to CSV file
    with open(os.path.join(output_dir, "resume_scores.csv") , 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Resume' ,'Skill score', 'Similarity Score %','Predicted Score'])
        for resume,skill_s , score ,label in ranked_resumes:
            writer.writerow([resume, skill_s,score,label])

    # set threshold 
    with open(os.path.join(output_dir, "best_resumes.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Resume' ,'Skill score', 'Similarity Score %','Predicted Score'])
        for resume,skill_s , score , label in ranked_resumes:
            if skill_s >=2 or score >= 50 :
                writer.writerow([resume, skill_s,score,label])


# Find best matching resume
def find_best_resume(resume_folder, job_description, output_path):
    # Read in resumes
    resumes , resume_names = load_resume(resume_folder)  
    # Extract features
    X , similarity_scores = extract_features(resumes, job_description)

    model = create_svr_model(X,similarity_scores)

    skill_scores = find_skill_score(resumes,job_description)

    # conert to per %
    similarity_factor = 100
    label_factor = 100
    similarity_scores = [round(score*similarity_factor) for score in similarity_scores]
    labels = [round(float(model.predict(data)) * label_factor) for data in X]


    ranked_resumes = sorted(zip(resume_names, skill_scores, similarity_scores, labels),key=lambda x: (-x[1], -x[2]))


    # save data csv file
    save_output_file(ranked_resumes,output_path)

    # Return best matching resume
    best_resume = ranked_resumes[0]
    return best_resume



resume_folder = '/home/indianic/Desktop/sentimate/resume_ranking/CVs'

# read job description
with open("job_description.txt","r") as f:
    data = f.read()
    job_description = re.sub(r'\s+', ' ', data).strip()

# Create a directory to store the output files
output_dir = 'resume_scores123'
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

best_resume = find_best_resume(resume_folder, job_description, output_dir)

print('Best matching resume :', best_resume[0])
print('Skill score :', best_resume[1])
print('Similarity score :', best_resume[2])
print('Precict score :',best_resume[3])
