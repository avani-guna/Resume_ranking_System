import re
from datetime import datetime
import os
import fitz


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
                # print(text)
                # print("------------------------------------------------------------------------------------------")
        resume_names.append(filename)
    return resumes , resume_names


def calculate_duration(text): 
    days = 0
    # text 1: Oct 2021 to Present
    # match = re.match(f'^{month_pattern} {year_pattern} to {present_pattern}$', text, re.IGNORECASE)
    try:
        pattern = r"\b\w{3}\s+\d{4}\s+to\s+(?:\b\w{3}\s+)?(?:\d{4}|Present)\b"
        match = re.search(pattern, text)
        if match:
            date = match.group(0).split('to')[0].strip()
            start_date = datetime.strptime(date, "%b %Y")
            end_date = datetime.now()
            days += (end_date - start_date).days
    except:
        pass

    # text 2: Feb 2021 to Sep 2021
    # match = re.match(f'^{month_pattern} {year_pattern} to {month_pattern} {year_pattern}$', text, re.IGNORECASE)
    pattern = r"(?:\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\s+to\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\s+to\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b)"
    match = re.findall(pattern, text)
    if match:
        for data in match:
            data = data.split(' to ')
            # print(data)
            # print("-----------------------------")
            if len(data[0]) == 8 and len(data[1]) == 8:
                start_date = datetime.strptime(data[0].strip(), '%b %Y')
                end_date = datetime.strptime(data[1].strip(), '%b %Y')
                days += (end_date - start_date).days
                
            elif len(data[0]) > 8 and len(data[1]) > 8:
                start_date = datetime.strptime(data[0].strip(), '%B %Y')
                end_date = datetime.strptime(data[1].strip(), '%B %Y')
               
                days += (end_date - start_date).days
            elif len(data[0]) == 8 and len(data[1]) > 8:
                start_date = datetime.strptime(data[0].strip(), '%b %Y')
                end_date = datetime.strptime(data[1].strip(), '%B %Y')
                days += (end_date - start_date).days
            else:
                start_date = datetime.strptime(data[0].strip(), '%B %Y')
                end_date = datetime.strptime(data[1].strip(), '%b %Y')
                days += (end_date - start_date).days 
                
   
    # NOV 2022 – JAN 2023
    # pattern = r"\b(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+\d{4}\b\s*(-|–)\s*\b(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+\d{4}\b"
    pattern = r"\b(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b\s*(?:–|-)\s*(?:January|February|March|April|May|June|July|August|September|October|November|December|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV)\s+\d{4}\b"
    
    match = re.findall(pattern, text)
    if match:
        for data in match:
            data = data.replace("–","-")
            data = data.split(" - ")
            if len(data[0]) == 8 and len(data[1]) == 8:
                start_date = datetime.strptime(data[0].strip(), '%b %Y')
                end_date = datetime.strptime(data[1].strip(), '%b %Y')
                days += (end_date - start_date).days
            elif len(data[0]) > 8 and len(data[1]) > 8:
                start_date = datetime.strptime(data[0].strip(), '%B %Y')
                end_date = datetime.strptime(data[1].strip(), '%B %Y')
                days += (end_date - start_date).days 
                
            elif len(data[0]) > 8 and len(data[1] == 8):
                start_date = datetime.strptime(data[0].strip(), '%B %Y')
                end_date = datetime.strptime(data[1].strip(), '%b %Y')
                days += (end_date - start_date).days
            
            else:
                start_date = datetime.strptime(data[0].strip(), '%b %Y')
                end_date = datetime.strptime(data[1].strip(), '%B %Y')
                days += (end_date - start_date).days
                
    # OCT-2022 - MARCH-2023' 
    pattern = r"\b(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)-\d{4}\b\s*-\s*\b(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)-\d{4}\b"
    match = re.findall(pattern, text)
    if match:
        for data in match:
            data = data.split(' - ')
            st = data[0].replace("-"," ")
            ed = data[1].replace("-"," ")
            if len(data[0]) == 8 and len(data[1]) == 8:
                start_date = datetime.strptime(st, '%b %Y')
                end_date = datetime.strptime(ed, '%b %Y')
                days += (end_date - start_date).days
            elif len(data[0]) > 8 and len(data[1] ==8):
                start_date = datetime.strptime(st, '%B %Y')
                end_date = datetime.strptime(ed, '%b %Y')
                days += (end_date - start_date).days
            elif len(data[0]) == 8 and len(data[1]) > 8:
                start_date = datetime.strptime(st, '%b %Y')
                end_date = datetime.strptime(ed, '%B %Y')
                days += (end_date - start_date).days
            else:
                start_date = datetime.strptime(st, '%B %Y')
                end_date = datetime.strptime(ed, '%B %Y')
                days += (end_date - start_date).days 

    try:
        # text 4: September 2019 – March 2022
        regex_pattern = r"(\w+ \d{4}) – (\w+ \d{4})"
        match = re.match(regex_pattern, text, re.IGNORECASE)
        if match:
            date = match.group(0).split('–')
            start_date = datetime.strptime(date[0].strip(), '%B %Y')
            end_date = datetime.strptime(date[1].strip(), '%B %Y')
            days += (end_date - start_date).days
    except:
        pass

    # text 5: September 2022 – present
    regex_pattern = r'^\w+ \d{4} – present$'
    match = re.match(regex_pattern, text, re.IGNORECASE)
    if match:
        date = match.group(0).split('–')
        start_date = datetime.strptime(date[0].strip(), '%B %Y')
        end_date = datetime.now()
        days += (end_date - start_date).days

    # text 6: 12/2022 – 02/2023
    pattern = r"\b\d{2}/\d{4}\s*–\s*\d{2}/\d{4}\b"
    match = re.findall(pattern, text)
    if match:
        for data in match[:1]:
            data = data.split(" – ")
            start_date = datetime.strptime(data[0], '%m/%Y')
            end_date = datetime.strptime(data[1], '%m/%Y')
            days += (end_date - start_date).days
    
    # If no text matched
    return days


if __name__ == "__main__":
    resume_folder = '/home/indianic/Desktop/sentimate/resume_ranking/AI_ML_CVs'
    resumes , resume_name = load_resume(resume_folder)
    total_exp = []
    for text in resumes:
        data = calculate_duration(text)
        print(data)
        total_exp.append(data)
    print(total_exp)