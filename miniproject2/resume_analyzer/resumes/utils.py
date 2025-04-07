# resumes/utils.py
import PyPDF2
import docx
import spacy
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.core.files import File
from users.models import CustomUser

from .schemas import ResumeAnalysis, Feedback

nlp = spacy.load("en_core_web_sm")

TRENDING_SKILLS = {
    'tech': ['python', 'javascript', 'react', 'aws', 'docker', 'sql', 'machine learning', 'typescript', 'kubernetes',
             'cloud'],
    'soft': ['communication', 'leadership', 'problem-solving', 'adaptability', 'collaboration']
}

ATS_KEYWORDS = [
    'experience', 'development', 'software', 'programming', 'team', 'project', 'management',
    'skills', 'technology', 'design', 'implementation', 'optimization', 'data', 'analysis'
]

def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            print(f"Extracted text from PDF: {text[:100]}...")
            return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        text = ""
        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"
        print(f"Extracted text from DOCX: {text[:100]}...")
        return text
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return ""

def process_resume(file_path):
    print(f"Processing file: {file_path}")

    if file_path.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")

    if not text:
        print("No text extracted from file")
        return ResumeAnalysis(
            skills="",
            experience="0 years",
            education="",
            rating=0.0,
            recommendations="Unable to extract text from resume",
            feedback=Feedback()
        ).dict()

    doc = nlp(text)
    text_lower = text.lower()
    print(f"Processed text: {text_lower[:100]}...")

    skills_keywords = [
        'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'django',
        'communication', 'teamwork', 'leadership', 'management', 'excel', 'aws',
        'docker', 'git', 'linux', 'agile', 'scrum', 'typescript', 'kubernetes',
        'cloud', 'machine learning', 'problem-solving', 'adaptability', 'collaboration'
    ]
    skills = set()
    for token in doc:
        if token.text.lower() in skills_keywords:
            skills.add(token.text.lower())
    for chunk in doc.noun_chunks:
        if chunk.text.lower() in skills_keywords:
            skills.add(chunk.text.lower())
    print(f"Extracted skills: {skills}")

    experience_years = 0
    experience_pattern = r'(\d+)\s*(?:year|yr|month|experience)'
    experience_matches = re.findall(experience_pattern, text_lower)
    for match in experience_matches:
        if match.isdigit():
            num = int(match)
            if num < 12 and 'month' in text_lower:
                experience_years += num / 12
            else:
                experience_years += num
    for ent in doc.ents:
        if ent.label_ == "DATE":
            if re.match(r'\d{4}\s*[-–—]\s*\d{4}', ent.text):
                start, end = map(int, re.findall(r'\d{4}', ent.text))
                experience_years += end - start
            elif re.match(r'\d{4}\s*[-–—]\s*present', ent.text.lower()):
                start = int(re.search(r'\d{4}', ent.text).group())
                experience_years += 2025 - start
    experience = f"{experience_years:.1f} years"
    print(f"Calculated experience: {experience}")

    education = set()
    education_keywords = [
        'bachelor', 'master', 'phd', 'degree', 'university', 'college',
        'bs', 'ms', 'ba', 'mba'
    ]
    for ent in doc.ents:
        if ent.label_ in ["ORG", "DATE"] and any(kw in ent.text.lower() for kw in education_keywords):
            education.add(ent.text)
        elif ent.label_ == "DATE" and re.match(r'\d{4}\s*[-–—]\s*\d{4}', ent.text):
            education.add(ent.text)
    print(f"Extracted education: {education}")

    skills_score = min(len(skills), 6) * 5
    if len(skills) > 6:
        skills_score += (len(skills) - 6) * 1
    skills_score = min(skills_score, 30)

    experience_score = min(experience_years * 3, 20)

    education_score = 0
    if any(kw in text_lower for kw in ['bachelor', 'bs', 'ba']):
        education_score += 10
    elif any(kw in text_lower for kw in ['master', 'ms', 'mba']):
        education_score += 15
    elif any(kw in text_lower for kw in ['phd']):
        education_score += 20
    if any(kw in text_lower for kw in ['university', 'college']):
        education_score += 5
    if re.search(r'\d{4}\s*[-–—]\s*\d{4}', text_lower):
        education_score += 5
    education_score = min(education_score, 20)

    rating = skills_score + experience_score + education_score
    print(f"Calculated rating: {rating}")

    feedback = Feedback(
        skill_gaps=[],
        formatting=[],
        ats_keywords=[]
    )
    missing_tech_skills = [skill for skill in TRENDING_SKILLS['tech'] if skill not in skills]
    missing_soft_skills = [skill for skill in TRENDING_SKILLS['soft'] if skill not in skills]
    if missing_tech_skills:
        feedback.skill_gaps.append(f"Missing trending technical skills: {', '.join(missing_tech_skills[:3])}")
    if missing_soft_skills:
        feedback.skill_gaps.append(f"Missing trending soft skills: {', '.join(missing_soft_skills[:2])}")

    sentences = [sent.text.strip() for sent in doc.sents]
    if len(sentences) < 5:
        feedback.formatting.append("Add more detailed descriptions to expand your resume")
    if len(text.split('\n')) < 10:
        feedback.formatting.append("Use more sections (e.g., Projects, Certifications) for better structure")
    if not re.search(r'\b\d+\b', text):
        feedback.formatting.append("Include quantifiable achievements (e.g., 'improved performance by 20%')")

    found_ats_keywords = [kw for kw in ATS_KEYWORDS if kw in text_lower]
    missing_ats_keywords = [kw for kw in ATS_KEYWORDS if kw not in text_lower]
    if len(found_ats_keywords) < len(ATS_KEYWORDS) * 0.5:
        feedback.ats_keywords.append(f"Add these ATS-friendly keywords: {', '.join(missing_ats_keywords[:3])}")
    print(f"Generated feedback: {feedback}")

    recommendations = []
    if len(skills) < 4:
        recommendations.append("Consider adding more technical skills to stand out")
    if experience_years < 1:
        recommendations.append("Try to gain more professional experience or include relevant projects")
    if education_score < 15:
        recommendations.append("Enhance your education section with more details")
    if len(sentences) < 5:
        recommendations.append("Expand your resume with more detailed descriptions")
    recommendations_text = '\n'.join(recommendations) if recommendations else "Well-structured resume!"
    print(f"Recommendations: {recommendations_text}")

    analysis = ResumeAnalysis(
        skills=', '.join(skills) if skills else "",
        experience=experience,
        education=', '.join(education) if education else "Not specified",
        rating=rating,
        recommendations=recommendations_text,
        feedback=feedback
    )
    print(f"Final analysis: {analysis.dict()}")
    return analysis.dict()

def process_job_description(description):

    doc = nlp(description.lower())

    skills_keywords = [
        'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'django',
        'communication', 'teamwork', 'leadership', 'management', 'excel', 'aws',
        'docker', 'git', 'linux', 'agile', 'scrum', 'typescript', 'kubernetes',
        'cloud', 'machine learning', 'problem-solving', 'adaptability', 'collaboration'
    ]
    required_skills = set()
    for token in doc:
        if token.text in skills_keywords:
            required_skills.add(token.text)


    experience_pattern = r'(\d+)\s*(?:year|yr|month|experience)'
    experience_matches = re.findall(experience_pattern, description.lower())
    required_experience = 0.0
    for match in experience_matches:
        if match.isdigit():
            num = int(match)
            if num < 12 and 'month' in description.lower():
                required_experience += num / 12
            else:
                required_experience += num

    return {
        'required_skills': required_skills,
        'required_experience': required_experience,
        'text': description
    }


def match_resume_to_job(resume, job):
    resume_skills = set(resume.skills.split(', ')) if resume.skills else set()
    job_skills = set(job.required_skills.split(', ')) if job.required_skills else set()

    resume_experience_str = resume.experience or "0 years"
    resume_experience = float(re.search(r'(\d+\.\d+|\d+)', resume_experience_str).group()) if re.search(
        r'(\d+\.\d+|\d+)', resume_experience_str) else 0.0

    job_experience_str = str(
        job.required_experience) if job.required_experience is not None else "0 years"
    job_experience = float(re.search(r'(\d+\.\d+|\d+)', job_experience_str).group()) if re.search(r'(\d+\.\d+|\d+)',
                                                                                                  job_experience_str) else 0.0

    common_skills = resume_skills.intersection(job_skills)
    skills_match = len(common_skills) / len(job_skills) if job_skills else 0
    skills_score = min(skills_match * 50, 50)

    experience_diff = resume_experience - job_experience
    if experience_diff >= 0:
        experience_score = min((resume_experience / job_experience) * 30, 30) if job_experience else 30
    else:
        experience_score = max(0, 30 + experience_diff * 5)

    try:
        tfidf = TfidfVectorizer(stop_words='english')
        resume_text = f"{resume.skills or ''} {resume.experience or ''} {resume.education or ''}"
        texts = [resume_text, job.description]
        tfidf_matrix = tfidf.fit_transform(texts)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        text_score = similarity * 20
    except Exception as e:
        print(f"TF-IDF error for resume {resume.id}: {str(e)}")
        text_score = 0

    compatibility_score = skills_score + experience_score + text_score

    try:
        user = CustomUser.objects.get(id=resume.user_id)
        username = user.username
    except CustomUser.DoesNotExist:
        username = "Unknown"

    return {
        'resume_id': str(resume.id),
        'user': username,
        'compatibility_score': round(compatibility_score, 2),
        'matched_skills': ', '.join(common_skills),
        'resume_skills': resume.skills,
        'resume_experience': resume.experience
    }