import pandas as pd
import numpy as np
import random

file_name = "demo_en.xlsx"
num_rows = 500  

teachers_list = ['Professor John Smith', 'Dr. Emily Davis', 'Professor Robert Johnson', 'Dr. Linda Kovalenko']
courses_list = ['1st Year (Bachelor)', '2nd Year (Bachelor)', '3rd Year (Bachelor)', '4th Year (Bachelor)', '1st Year (Master)']

columns = [
    'Timestamp',
    'How clearly did the professor present the course syllabus and requirements during the first class?',
    'How do you evaluate the professor’s organizational culture (punctuality, time management)?',
    'Did you have seamless access to the course syllabus on the university website?',
    'How objective and transparent were the grading criteria?',
    'How clearly, logically, and comprehensibly did the professor deliver the material?',
    'How do you rate the quality and completeness of the course content in Moodle?',
    'Were innovative teaching methods utilized during classes (discussions, group work)?',
    'Did the professor regularly inform you about your accumulated grading points?',
    'How deeply does the professor demonstrate mastery of the subject and broad erudition?',
    'How effectively does the professor bridge theoretical concepts with practical tasks?',
    'How polite, respectful, and tactful was the professor in personal communication?',
    'How do you evaluate the professor’s speech patterns and delivery pace?',
    'Did the professor foster a comfortable learning environment for everyone?',
    'Was the professor available for consultative support outside of class hours?',
    'Which communication channels proved most effective for you personally?',
    'What main challenges or difficulties did you face while studying this course?',
    'Did you engage in academic dishonesty (cheating) during quizzes or exams?',
    'Were plagiarism checks conducted on your written assignments?',
    'Did you face any instances of academic corruption during this session?',
    'What did you enjoy most about this educational course?',
    'What did you dislike most, and what improvements would you suggest?'
]

opts_polite = ['Always respectful and friendly', 'Mostly respectful, with rare exceptions', 'Occasionally permitted inappropriate remarks', 'Frequently unprofessional or unwelcoming']
opts_speech = ['Excellent (articulate, clear delivery)', 'Satisfactory (generally understandable)', 'Poor (confusing phrasing, too fast/slow)', 'Unsatisfactory (difficult to comprehend)']
opts_comfort = ['Yes, absolutely comfortable', 'Mostly comfortable, with minor drawbacks', 'Rather stressful than comfortable', 'No, the atmosphere was highly tense']
opts_consult = ['Yes, always open to communication', 'Mostly yes, but with certain restrictions', 'Occasionally provided support, but it was difficult', 'No, out-of-class consultation was impossible']
opts_comm = ['Telegram', 'Viber', 'Email', 'Moodle', 'Zoom', 'In Person', 'Google Meet', 'WhatsApp', 'Teams', np.nan] 
opts_diff = ['Lack of time', 'Complex material', 'Technical issues', 'Unclear requirements', 'Excessive workload', 'Tight deadlines', 'None', np.nan]
opts_liked = ['Professor', 'Lectures', 'Practical Tasks', 'Quizzes & Tests', 'Everything', 'Nothing', 'Presentations', 'Video Materials', 'Accessibility', np.nan]
opts_disliked = ['Too many tasks', 'Complex tests', 'Boring lectures', 'Nothing', 'Everything', 'Insufficient practice', 'Too much theory', 'Schedule issues', np.nan]

data = {}

# Timestamps
start_date = pd.to_datetime('2025-09-01')
end_date = pd.to_datetime('2025-10-31')
seconds_range = (end_date - start_date).total_seconds()
random_seconds = np.random.randint(0, int(seconds_range), num_rows)
data[columns[0]] = start_date + pd.to_timedelta(random_seconds, unit='s')

# Demographic Filters
data['Select your course'] = [random.choice(courses_list) for _ in range(num_rows)]
data['Select professor'] = [random.choice(teachers_list) for _ in range(num_rows)]

# Likert Scales (1-5)
likert_indices = [1, 2, 3, 4, 5, 6, 9, 10]
for i in likert_indices:
    p_dist = np.random.dirichlet(np.ones(5)*3)
    data[columns[i]] = np.random.choice([1, 2, 3, 4, 5], size=num_rows, p=p_dist)

# Categorical & Text mapping
data[columns[7]] = np.random.choice(['Hard to answer', 'No', 'Yes'], size=num_rows, p=[0.2, 0.3, 0.5])
data[columns[8]] = np.random.choice(['Hard to answer', 'Yes', 'No'], size=num_rows, p=[0.1, 0.7, 0.2])
data[columns[11]] = np.random.choice(opts_polite, size=num_rows, p=[0.6, 0.25, 0.1, 0.05])
data[columns[12]] = np.random.choice(opts_speech, size=num_rows, p=[0.55, 0.3, 0.1, 0.05])
data[columns[13]] = np.random.choice(opts_comfort, size=num_rows, p=[0.5, 0.35, 0.1, 0.05])
data[columns[14]] = np.random.choice(opts_consult, size=num_rows, p=[0.45, 0.3, 0.2, 0.05])
data[columns[15]] = np.random.choice(opts_comm, size=num_rows, p=[0.35, 0.1, 0.15, 0.15, 0.05, 0.05, 0.05, 0.05, 0.025, 0.025])
data[columns[16]] = np.random.choice(opts_diff, size=num_rows)
data[columns[17]] = np.random.choice(['Yes', 'No'], size=num_rows, p=[0.3, 0.7])
data[columns[18]] = np.random.choice(['Yes', 'No', 'Don\'t know'], size=num_rows, p=[0.6, 0.2, 0.2])
data[columns[19]] = np.random.choice(['No', 'Decline to answer', 'Yes'], size=num_rows, p=[0.9, 0.08, 0.02])
data[columns[20]] = np.random.choice(opts_liked, size=num_rows)
data[columns[21]] = np.random.choice(opts_disliked, size=num_rows)

df = pd.DataFrame(data)

# Reordering (Timestamp -> Filters -> Questions)
cols = list(df.columns)
new_order = [cols[0], 'Select your course', 'Select professor'] + [c for c in cols if c not in [cols[0], 'Select your course', 'Select professor']]
df = df[new_order]

df.to_excel(file_name, index=False)
print(f"✅ Demo file '{file_name}' generated successfully with {num_rows} rows.")