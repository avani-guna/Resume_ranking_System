import spacy
import pickle
import random
from spacy.training.example import Example
import os
import fitz

def train_model():
    train_data = pickle.load(open('train_data.pkl', 'rb'))
    nlp = spacy.blank('en')
    ner = nlp.add_pipe('ner')

    for _, annotation in train_data:
        for ent in annotation['entities']:
            ner.add_label(ent[2])

    optimizer = nlp.initialize()
    for itn in range(10):
        print("Starting iteration " + str(itn))
        random.shuffle(train_data)
        losses = {}
        for text, annotations in train_data:
            try:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                nlp.update(
                    [example],
                    drop=0.2,
                    sgd=optimizer,
                    losses=losses)
            except Exception as e:
                pass

        print(losses)

    nlp.to_disk('nlp_model')

nlp_model = spacy.load('nlp_model')

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

resumes,_ = load_resume('/home/indianic/Desktop/sentimate/resume_ranking/AI_ML_CVs')

for text in resumes:
    doc = nlp_model(text)
    for ent in doc.ents:
        print(f'{ent.label_.upper():{30}}- {ent.text}')
    print("###"*50)