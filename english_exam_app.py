import sqlite3
import json
import os
import pandas as pd
import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Hệ thống Ôn thi Tuyển sinh 10 Tiếng Anh TP.HCM",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database Setup
DB_FILE = "exam_results.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            student_info TEXT NOT NULL,
            score REAL NOT NULL,
            max_score REAL NOT NULL,
            submitted_at TEXT NOT NULL,
            answers_json TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Custom CSS for Modern, Colorful, and Responsive UI
CUSTOM_CSS = """
<style>
/* Main Background & Font */
.stApp {
    background-color: #f8fafc;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Custom Main Header Banner */
.main-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #2563eb 100%);
    color: white;
    padding: 2.2rem 2rem;
    border-radius: 18px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25);
    text-align: center;
}

.main-header h1 {
    color: #ffffff !important;
    font-weight: 800;
    font-size: 2.2rem;
    margin-bottom: 0.6rem;
    letter-spacing: -0.5px;
}

.main-header p {
    color: #93c5fd !important;
    font-size: 1.1rem;
    margin-bottom: 0;
    font-weight: 500;
}

/* Section Header Badges */
.section-header {
    background: linear-gradient(90deg, #1e293b 0%, #334155 100%);
    color: #ffffff !important;
    padding: 0.8rem 1.4rem;
    border-radius: 12px;
    font-size: 1.2rem;
    font-weight: 700;
    margin-top: 2rem;
    margin-bottom: 1.2rem;
    border-left: 6px solid #3b82f6;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
}

/* Reading Passage & Notice Boxes */
.passage-box {
    background-color: #ffffff;
    border-left: 5px solid #0284c7;
    border-right: 1px solid #e2e8f0;
    border-top: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    padding: 1.4rem 1.6rem;
    border-radius: 12px;
    font-size: 1.05rem;
    line-height: 1.75;
    color: #1e293b;
    margin-bottom: 1.8rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
}

.notice-sign-box {
    background-color: #fffbeb;
    border: 2px dashed #f59e0b;
    padding: 1.2rem;
    border-radius: 12px;
    text-align: center;
    font-family: 'Courier New', Courier, monospace;
    font-size: 1.05rem;
    font-weight: 700;
    color: #78350f;
    margin: 1rem 0;
}

/* Question Badges */
.q-badge {
    background-color: #eff6ff;
    color: #1d4ed8;
    font-weight: 700;
    font-size: 0.9rem;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    border: 1px solid #bfdbfe;
    display: inline-block;
    margin-bottom: 0.6rem;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}

/* Hide Streamlit default top padding */
.block-container {
    padding-top: 2rem !important;
}
</style>
"""

# Questions Data
QUESTIONS = [
    # I. MULTIPLE CHOICE
    {
        "id": 1,
        "type": "mcq",
        "part": "I. MULTIPLE CHOICE (Phát âm & Trọng âm)",
        "question": "Choose the word whose <u>underlined part</u> differs from the other three in pronunciation:",
        "options_display": [
            "A. miss<u><b>ed</b></u>",
            "B. liv<u><b>ed</b></u>",
            "C. cook<u><b>ed</b></u>",
            "D. stopp<u><b>ed</b></u>"
        ],
        "answer": "B. lived",
        "explanation": "Đuôi '<u><b>ed</b></u>' trong 'lived' được phát âm là /d/ (/lɪvd/). Ở các từ còn lại, đuôi 'ed' đứng sau âm vô thanh (/s/, /k/, /p/) nên được phát âm là /t/ (/mɪst/, /kʊkt/, /stɒpt/)."
    },
    {
        "id": 2,
        "type": "mcq",
        "part": "I. MULTIPLE CHOICE (Phát âm & Trọng âm)",
        "question": "Choose the word whose <u>underlined part</u> differs from the other three in pronunciation:",
        "options_display": [
            "A. cl<u><b>i</b></u>mate",
            "B. l<u><b>i</b></u>tter",
            "C. v<u><b>i</b></u>llage",
            "D. hab<u><b>i</b></u>t"
        ],
        "answer": "A. climate",
        "explanation": "Chữ '<u><b>i</b></u>' trong 'climate' phát âm là âm đôi /aɪ/ (/ˈklaɪ.mət/). Ở các từ còn lại, chữ 'i' phát âm là âm ngắn /ɪ/ (/ˈlɪt.ər/, /ˈvɪl.ɪdʒ/, /ˈhæb.ɪt/)."
    },
    {
        "id": 3,
        "type": "mcq",
        "part": "I. MULTIPLE CHOICE (Phát âm & Trọng âm)",
        "question": "Choose the word that differs from the other three in the position of primary stress:",
        "options_display": ["A. reduce", "B. suggest", "C. offer", "D. protect"],
        "answer": "C. offer",
        "explanation": "'offer' có trọng âm rơi vào âm tiết thứ 1 (/ˈɒf.ər/). Các từ còn lại có trọng âm rơi vào âm tiết thứ 2 (re'duce, sug'gest, pro'tect)."
    },
    {
        "id": 4,
        "type": "mcq",
        "part": "I. MULTIPLE CHOICE (Phát âm & Trọng âm)",
        "question": "Choose the word that differs from the other three in the position of primary stress:",
        "options_display": ["A. decision", "B. pollution", "C. energy", "D. official"],
        "answer": "C. energy",
        "explanation": "'energy' có trọng âm rơi vào âm tiết thứ 1 (/ˈen.ə.dʒi/). Các từ còn lại có trọng âm rơi vào âm tiết thứ 2 (de'cision, pol'lution, of'ficial)."
    },
    {
        "id": 5,
        "type": "mcq",
        "part": "I. MULTIPLE CHOICE (Ngữ pháp & Từ vựng)",
        "question": "Linh recently moved to a busy district in Ho Chi Minh City. She finds it hard to sleep because she is not used ______ to the constant noise of vehicles at night.",
        "options_display": ["A. to listen", "B. to listening", "C. for listening", "D. listen"],
        "answer": "B. to listening",
        "explanation": "Cấu trúc 'be used to + V-ing' diễn tả sự quen thuộc với việc gì ở hiện tại. (Phân biệt với 'used to + V0' chỉ thói quen quá khứ)."
    },
    {
        "id": 6,
        "type": "mcq",
        "part": "I. MULTIPLE CHOICE (Ngữ pháp & Từ vựng)",
        "question": "During the job interview at a tech company in District 1, the manager asked Minh ______ in digital marketing before applying for this position.",
        "options_display": [
            "A. how many years of experience had he got",
            "B. how many years of experience he had got",
            "C. if had he got experience",
            "D. that he had got any experience"
        ],
        "answer": "B. how many years of experience he had got",
        "explanation": "Trong câu tường thuật dạng câu hỏi Wh-question, ta đưa trật tự từ về dạng câu trần thuật (Subject + Verb), lùi thì và tuyệt đối không đảo trợ động từ lên trước chủ ngữ."
    },
    {
        "id": 7,
        "type": "mcq",
        "part": "I. MULTIPLE CHOICE (Ngữ pháp & Từ vựng)",
        "question": "You should bring an umbrella with you ______ it rains heavily during our eco-tour in Can Gio mangrove forest this afternoon.",
        "options_display": ["A. if", "B. in case", "C. unless", "D. provided"],
        "answer": "B. in case",
        "explanation": "'In case' (phòng khi) dùng chỉ hành động mang tính phòng ngừa trước một khả năng có thể xảy ra."
    },
    {
        "id": 8,
        "type": "mcq",
        "part": "I. MULTIPLE CHOICE (Ngữ pháp & Từ vựng)",
        "question": "I have so much revision to finish for the upcoming exam. I wish I ______ join my classmates for the charity fair in the school yard today.",
        "options_display": ["A. would", "B. could", "C. can", "D. will"],
        "answer": "B. could",
        "explanation": "Câu ước ở hiện tại cho khả năng của bản thân (I wish I) bắt buộc dùng 'could + V0', không dùng 'would'."
    },
    {
        "id": 9,
        "type": "mcq",
        "part": "I. MULTIPLE CHOICE (Ngữ pháp & Từ vựng)",
        "question": "______ the severe traffic congestion on Cong Hoa Street during peak hours, the express bus arrived at the station right on time.",
        "options_display": ["A. Although", "B. In spite", "C. Despite of", "D. In spite of"],
        "answer": "D. In spite of",
        "explanation": "'In spite of + Noun Phrase'. Lưu ý 'Despite' KHÔNG đi với 'of' (đáp án C sai ngữ pháp)."
    },
    {
        "id": 10,
        "type": "mcq",
        "part": "I. MULTIPLE CHOICE (Ngữ pháp & Từ vựng)",
        "question": "Many rare species of birds ______ to have returned to the Dong Nai Nature Reserve after recent reforestation efforts.",
        "options_display": ["A. report", "B. are reported", "C. are reporting", "D. have reported"],
        "answer": "B. are reported",
        "explanation": "Cấu trúc bị động với động từ chỉ ý kiến/báo cáo: S + be + V3 + to-V."
    },
    {
        "id": 11,
        "type": "mcq",
        "part": "I. MULTIPLE CHOICE (Ngữ pháp & Từ vựng)",
        "question": "The school STEM project was ______ a great success that all visitors expressed their admiration for the young inventors.",
        "options_display": ["A. so", "B. such", "C. too", "D. enough"],
        "answer": "B. such",
        "explanation": "Cấu trúc chỉ kết quả: 'such + a/an + Adj + Noun + that'."
    },
    {
        "id": 12,
        "type": "mcq",
        "part": "I. MULTIPLE CHOICE (Giao tiếp)",
        "question": "Nam and Mai are discussing ways to reduce plastic waste at school.\n- Nam: 'Why don't we bring reusable thermos flasks to school every day?'\n- Mai: '______ That will significantly cut down on single-use plastic cups.'",
        "options_display": ["A. You're welcome.", "B. I couldn't agree more!", "C. Never mind.", "D. It's my pleasure."],
        "answer": "B. I couldn't agree more!",
        "explanation": "'I couldn't agree more!' (Tôi hoàn toàn đồng ý!) thể hiện sự tán thành mạnh mẽ đối với ý kiến vừa đưa ra."
    },
    {
        "id": 13,
        "type": "mcq",
        "part": "I. MULTIPLE CHOICE (Biển báo & Thông báo)",
        "question": "Look at the notice below. What does it tell you?",
        "notice_html": "<div class='notice-sign-box'>📌 NOTICE: LIBRARY QUIET ZONE<br>Please turn off your mobile phones or switch them to silent mode before entering the room.</div>",
        "options_display": [
            "A. Mobile phones are completely forbidden inside the library.",
            "B. Visitors must ensure their phones do not make noise in this area.",
            "C. You are allowed to make phone calls if you speak in a low voice.",
            "D. All electronic devices must be handed over to the librarian."
        ],
        "answer": "B. Visitors must ensure their phones do not make noise in this area.",
        "explanation": "Thông báo yêu cầu tắt điện thoại hoặc để im lặng để giữ trật tự trong thư viện."
    },
    {
        "id": 14,
        "type": "mcq",
        "part": "I. MULTIPLE CHOICE (Biển báo & Thông báo)",
        "question": "Look at the warning sign below. What does it mean?",
        "notice_html": "<div class='notice-sign-box' style='background-color: #fef2f2; border-color: #ef4444; color: #991b1b;'>⚠️ WARNING: SLIPPERY SURFACE WHEN WET<br>Please watch your step!</div>",
        "options_display": [
            "A. The floor is currently dry and safe for running.",
            "B. People should walk carefully because the surface can cause slips when wet.",
            "C. Water is strictly prohibited in this corridor.",
            "D. Pedestrians must wear special boots before stepping here."
        ],
        "answer": "B. People should walk carefully because the surface can cause slips when wet.",
        "explanation": "Biển cảnh báo mặt sàn trơn trượt khi bị ướt, nhắc nhở đi đứng cẩn thận."
    },

    # II. CLOZE TEST
    {
        "id": 15,
        "type": "mcq",
        "part": "II. CLOZE TEST (Lối sống xanh)",
        "question": "Question 15: Choose the best answer to fill in blank (15):",
        "options_display": ["A. However", "B. For instance", "C. Therefore", "D. Otherwise"],
        "answer": "B. For instance",
        "explanation": "'For instance' (Ví dụ như) đưa ra ví dụ minh họa cho nhận thức 'hành động nhỏ có tác động lớn' ở câu trước."
    },
    {
        "id": 16,
        "type": "mcq",
        "part": "II. CLOZE TEST (Lối sống xanh)",
        "question": "Question 16: Choose the best answer to fill in blank (16):",
        "options_display": ["A. by", "B. for", "C. with", "D. on"],
        "answer": "A. by",
        "explanation": "'by + V-ing' chỉ phương thức/cách thức (khuyến khích bằng cách giảm giá)."
    },
    {
        "id": 17,
        "type": "mcq",
        "part": "II. CLOZE TEST (Lối sống xanh)",
        "question": "Question 17: Choose the best answer to fill in blank (17):",
        "options_display": ["A. Although", "B. Because of", "C. In spite of", "D. Because"],
        "answer": "C. In spite of",
        "explanation": "'In spite of + Noun Phrase' (In spite of the hot weather) thể hiện sự nhượng bộ."
    },
    {
        "id": 18,
        "type": "mcq",
        "part": "II. CLOZE TEST (Lối sống xanh)",
        "question": "Question 18: Choose the best answer to fill in blank (18):",
        "options_display": ["A. take", "B. took", "C. had taken", "D. will take"],
        "answer": "B. took",
        "explanation": "Câu điều kiện loại 2 giả định ở hiện tại: If + S + V2/ed ('took')."
    },
    {
        "id": 19,
        "type": "mcq",
        "part": "II. CLOZE TEST (Lối sống xanh)",
        "question": "Question 19: Choose the best answer to fill in blank (19):",
        "options_display": ["A. about", "B. for", "C. with", "D. in"],
        "answer": "A. about",
        "explanation": "Cụm từ 'educate somebody about something' (giáo dục ai về việc gì)."
    },
    {
        "id": 20,
        "type": "mcq",
        "part": "II. CLOZE TEST (Lối sống xanh)",
        "question": "Question 20: Choose the best answer to fill in blank (20):",
        "options_display": ["A. practice", "B. practicing", "C. practiced", "D. to practice"],
        "answer": "B. practicing",
        "explanation": "Cấu trúc 'get used to + V-ing' (dần quen với việc làm gì)."
    },

    # III. READING COMPREHENSION
    {
        "id": 21,
        "type": "mcq",
        "part": "III. READING COMPREHENSION (Chuyển đổi số trong học Tiếng Anh)",
        "question": "Question 21: 'Online learning platforms have become vital resources for entrance exam preparation in Vietnam.' - Is this statement True or False?",
        "options_display": ["True", "False"],
        "answer": "True",
        "explanation": "Trích đoạn 1: 'Online learning platforms and digital resource libraries have become essential tools for both teachers and students preparing for important entrance examinations.'"
    },
    {
        "id": 22,
        "type": "mcq",
        "part": "III. READING COMPREHENSION (Chuyển đổi số trong học Tiếng Anh)",
        "question": "Question 22: 'Automated feedback systems force students to wait several days to identify their test errors.' - Is this statement True or False?",
        "options_display": ["True", "False"],
        "answer": "False",
        "explanation": "Trích đoạn 2: 'automated feedback systems allow students to identify their mistakes immediately...' (Hệ thống phản hồi tự động giúp học sinh biết lỗi sai ngay lập tức, không phải chờ nhiều ngày)."
    },
    {
        "id": 23,
        "type": "mcq",
        "part": "III. READING COMPREHENSION (Chuyển đổi số trong học Tiếng Anh)",
        "question": "Question 23: 'Social media distraction is one of the obstacles students face during online self-study.' - Is this statement True or False?",
        "options_display": ["True", "False"],
        "answer": "True",
        "explanation": "Trích đoạn 3: 'Without self-discipline, students may easily get distracted by social media or online games during self-study sessions.'"
    },
    {
        "id": 24,
        "type": "mcq",
        "part": "III. READING COMPREHENSION (Chuyển đổi số trong học Tiếng Anh)",
        "question": "Question 24: 'Educational experts advise against combining online learning with traditional classroom instruction.' - Is this statement True or False?",
        "options_display": ["True", "False"],
        "answer": "False",
        "explanation": "Trích đoạn 3: 'combining online self-study with traditional classroom interaction... remains the most effective strategy...' (Chuyên gia đánh giá mô hình kết hợp blended learning là hiệu quả nhất, không hề khuyên phản đối)."
    },
    {
        "id": 25,
        "type": "mcq",
        "part": "III. READING COMPREHENSION (Chuyển đổi số trong học Tiếng Anh)",
        "question": "Question 25: The word 'flexibility' in paragraph 2 is closest in meaning to:",
        "options_display": ["A. difficulty", "B. adaptability", "C. strictness", "D. weakness"],
        "answer": "B. adaptability",
        "explanation": "'flexibility' có nghĩa là sự linh hoạt, khả năng thích ứng (adaptability)."
    },
    {
        "id": 26,
        "type": "mcq",
        "part": "III. READING COMPREHENSION (Chuyển đổi số trong học Tiếng Anh)",
        "question": "Question 26: What is the main idea of the passage?",
        "options_display": [
            "A. The history of printed textbooks in Vietnamese secondary schools.",
            "B. The benefits and challenges of digital English learning for students.",
            "C. Why students should completely replace classroom learning with smartphones.",
            "D. How parents can teach English grammar to their children at home."
        ],
        "answer": "B. The benefits and challenges of digital English learning for students.",
        "explanation": "Nội dung bài viết tổng hợp cả các lợi ích (Đoạn 2) lẫn thách thức (Đoạn 3) của việc học tiếng Anh trực tuyến."
    },

    # IV. WORD FORMATION
    {
        "id": 27,
        "type": "text",
        "part": "IV. WORD FORMATION",
        "question": "Question 27: The school board decided to ____________ the main gate road to avoid traffic jams during peak hours. (WIDE)",
        "answer": "widen",
        "accepted_answers": ["widen"],
        "explanation": "Sau 'decided to' cần một Động từ nguyên mẫu: 'widen' (mở rộng)."
    },
    {
        "id": 28,
        "type": "text",
        "part": "IV. WORD FORMATION",
        "question": "Question 28: Environmentalists are deeply concerned about the severe ____________ of air quality in industrial zones. (POLLUTE)",
        "answer": "pollution",
        "accepted_answers": ["pollution"],
        "explanation": "Sau tính từ 'severe' cần một Danh từ: 'pollution' (sự ô nhiễm)."
    },
    {
        "id": 29,
        "type": "text",
        "part": "IV. WORD FORMATION",
        "question": "Question 29: The tour guide gave a very ____________ explanation about the historic architecture of the Saigon Central Post Office. (INFORM)",
        "answer": "informative",
        "accepted_answers": ["informative"],
        "explanation": "Đứng trước danh từ 'explanation' cần một Tính từ: 'informative' (cung cấp nhiều thông tin bổ ích)."
    },
    {
        "id": 30,
        "type": "text",
        "part": "IV. WORD FORMATION",
        "question": "Question 30: Thousands of high school volunteers ____________ participated in the city's green campaign last Sunday. (ENTHUSIASTIC)",
        "answer": "enthusiastically",
        "accepted_answers": ["enthusiastically"],
        "explanation": "Bổ nghĩa cho động từ 'participated' cần một Trạng từ: 'enthusiastically' (một cách hào hứng)."
    },
    {
        "id": 31,
        "type": "text",
        "part": "IV. WORD FORMATION",
        "question": "Question 31: Regular physical exercise and a balanced diet are key factors to improve your overall health and ____________. (STRONG)",
        "answer": "strength",
        "accepted_answers": ["strength"],
        "explanation": "Sau liên từ 'and' kết hợp với danh từ 'health' cần một Danh từ tương đương: 'strength' (sức mạnh/thể lực)."
    },
    {
        "id": 32,
        "type": "text",
        "part": "IV. WORD FORMATION",
        "question": "Question 32: It is ____________ to ride motorbikes on the pedestrian pavement, and violators will be heavily fined. (LEGAL)",
        "answer": "illegal",
        "accepted_answers": ["illegal"],
        "explanation": "Dựa vào ngữ cảnh phạt nặng, cần Tính từ mang nghĩa phủ định: 'illegal' (bất hợp pháp/trái pháp luật)."
    },

    # V. SENTENCE REARRANGEMENT
    {
        "id": 33,
        "type": "text",
        "part": "V. SENTENCE REARRANGEMENT",
        "question": "Question 33: Rearrange the words: 'Students should / in order to / bring reusable water bottles / single-use plastic waste / reduce / .'\n👉 Start with: Students...",
        "answer": "Students should bring reusable water bottles in order to reduce single-use plastic waste.",
        "accepted_answers": [
            "students should bring reusable water bottles in order to reduce single-use plastic waste.",
            "students should bring reusable water bottles in order to reduce single-use plastic waste"
        ],
        "explanation": "Cấu trúc chỉ mục đích: S + should + V0 + in order to + V0."
    },
    {
        "id": 34,
        "type": "text",
        "part": "V. SENTENCE REARRANGEMENT",
        "question": "Question 34: Rearrange the words: 'save energy / If everyone / turns off unnecessary lights / protect the environment / , / we can / and / .'\n👉 Start with: If everyone...",
        "answer": "If everyone turns off unnecessary lights, we can save energy and protect the environment.",
        "accepted_answers": [
            "if everyone turns off unnecessary lights, we can save energy and protect the environment.",
            "if everyone turns off unnecessary lights, we can save energy and protect the environment"
        ],
        "explanation": "Câu điều kiện loại 1 diễn tả khả năng thực tế ở hiện tại/tương lai."
    },

    # VI. SENTENCE TRANSFORMATION
    {
        "id": 35,
        "type": "text",
        "part": "VI. SENTENCE TRANSFORMATION",
        "question": "Question 35: I am sorry that I cannot attend your English speaking club meeting this Saturday.\n👉 Rewrite: I wish...",
        "answer": "I wish I could attend your English speaking club meeting this Saturday.",
        "accepted_answers": [
            "i wish i could attend your english speaking club meeting this saturday.",
            "i wish i could attend your english speaking club meeting this saturday"
        ],
        "explanation": "Ước cho khả năng ở hiện tại/tương lai dùng 'wish + S + could + V0'."
    },
    {
        "id": 36,
        "type": "text",
        "part": "VI. SENTENCE TRANSFORMATION",
        "question": "Question 36: Lan doesn't have a personal laptop, so she cannot join the online group discussion tonight.\n👉 Rewrite: If Lan...",
        "answer": "If Lan had a personal laptop, she could join the online group discussion tonight.",
        "accepted_answers": [
            "if lan had a personal laptop, she could join the online group discussion tonight.",
            "if lan had a personal laptop, she could join the online group discussion tonight"
        ],
        "explanation": "Giả định trái thực tế ở hiện tại dùng Câu điều kiện loại 2: If + S + V2/ed, S + could + V0."
    },
    {
        "id": 37,
        "type": "text",
        "part": "VI. SENTENCE TRANSFORMATION",
        "question": "Question 37: 'If I were you, I would spend more time practicing listening comprehension,' Mr. Tuan said to Minh.\n👉 Rewrite: Mr. Tuan advised...",
        "answer": "Mr. Tuan advised Minh to spend more time practicing listening comprehension.",
        "accepted_answers": [
            "mr. tuan advised minh to spend more time practicing listening comprehension.",
            "mr. tuan advised minh to spend more time practicing listening comprehension"
        ],
        "explanation": "Lời khuyên 'If I were you...' chuyển sang câu gián tiếp viết lại thành 'advised + O + to-V'."
    },
    {
        "id": 38,
        "type": "text",
        "part": "VI. SENTENCE TRANSFORMATION",
        "question": "Question 38: A professional technician repaired my father's air conditioner yesterday afternoon.\n👉 Rewrite: My father had...",
        "answer": "My father had his air conditioner repaired by a professional technician yesterday afternoon.",
        "accepted_answers": [
            "my father had his air conditioner repaired by a professional technician yesterday afternoon.",
            "my father had his air conditioner repaired by a professional technician yesterday afternoon"
        ],
        "explanation": "Cấu trúc bị động truyền sai (Causative Passive): 'have + something + V3/ed + (by O)'."
    },
    {
        "id": 39,
        "type": "text",
        "part": "VI. SENTENCE TRANSFORMATION",
        "question": "Question 39: Although the weather was extremely rainy, the outdoor music concert was not cancelled.\n👉 Rewrite: In spite of...",
        "answer": "In spite of the extremely rainy weather, the outdoor music concert was not cancelled.",
        "accepted_answers": [
            "in spite of the extremely rainy weather, the outdoor music concert was not cancelled.",
            "in spite of the extremely rainy weather, the outdoor music concert was not cancelled",
            "in spite of the fact that the weather was extremely rainy, the outdoor music concert was not cancelled.",
            "in spite of the fact that the weather was extremely rainy, the outdoor music concert was not cancelled"
        ],
        "explanation": "Chuyển từ mệnh đề 'Although + S + be + Adj' sang cụm danh từ 'In spite of + Noun Phrase'."
    },
    {
        "id": 40,
        "type": "text",
        "part": "VI. SENTENCE TRANSFORMATION",
        "question": "Question 40: The suitcase was so heavy that the young boy couldn't lift it onto the luggage rack.\n👉 Rewrite: The suitcase was too...",
        "answer": "The suitcase was too heavy for the young boy to lift onto the luggage rack.",
        "accepted_answers": [
            "the suitcase was too heavy for the young boy to lift onto the luggage rack.",
            "the suitcase was too heavy for the young boy to lift onto the luggage rack"
        ],
        "explanation": "Chuyển từ 'so...that' sang 'too...to': 'too + Adj + for O + to-V' (Bắt buộc lược bỏ tân ngữ 'it' ở cuối câu)."
    }
]

# Render Custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# App Header Banner
st.markdown("""
<div class="main-header">
    <h1>🎓 ĐỀ THI TUYỂN SINH LỚP 10 THPT MÔN TIẾNG ANH</h1>
    <p>Hệ thống Làm bài & Chấm điểm Tự động — Sở GD&ĐT TP. Hồ Chí Minh (Cấu trúc 2026 - 2027)</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("📌 Danh mục")
mode = st.sidebar.radio("Chọn chức năng:", ["📝 Làm bài thi", "📜 Lịch sử bài làm", "🔑 Quản trị viên (Admin)"])

# Passages Texts
CLOZE_PASSAGE = """
<div class="passage-box">
    <h4 style="color: #0369a1; margin-bottom: 0.8rem;">📖 PASSAGE FOR CLOZE TEST (Questions 15 – 20)</h4>
    In recent years, many young citizens in Ho Chi Minh City have started adopting greener lifestyles to protect the environment. They realize that small daily actions can lead to positive environmental impacts. <b>(15)</b> ______, many students now choose to commute by public electric buses or bicycles instead of personal motorbikes.<br><br>
    Additionally, teenagers are becoming more conscious of single-use plastic waste. Instead of buying disposable bottles, they carry personal water containers. Many coffee shops in the city also encourage this trend <b>(16)</b> ______ offering discounts to customers who bring their own cups.<br><br>
    Community groups regularly organize weekend clean-up campaigns along local canals. <b>(17)</b> ______ the hot weather, hundreds of volunteers gather enthusiastically to collect garbage and sort recyclable materials. A high school student participating in last Sunday's event shared that if more citizens <b>(18)</b> ______ part in such community activities, the city would become much cleaner and more liveable.<br><br>
    Furthermore, local authorities are planning to install smart recycling bins in major parks to educate the public <b>(19)</b> ______ waste separation at source. It is hoped that every resident will soon get used to <b>(20)</b> ______ green habits as a normal part of their daily routine.
</div>
"""

READING_PASSAGE = """
<div class="passage-box">
    <h4 style="color: #0369a1; margin-bottom: 0.8rem;">📖 READING PASSAGE (Questions 21 – 26)</h4>
    Digital technology has transformed English language education across Vietnam, particularly in major urban centers. Online learning platforms and digital resource libraries have become essential tools for both teachers and students preparing for important entrance examinations.<br><br>
    One significant advantage of digital learning is flexibility. Students can access interactive grammar exercises, vocabulary flashcards, and practice tests anytime from home. Rather than relying solely on traditional printed textbooks, learners can pause, review, and re-attempt exercises until they fully understand complex grammar points like reported speech or conditional clauses. Moreover, automated feedback systems allow students to identify their mistakes immediately, helping them correct grammatical misunderstandings without waiting for teacher assessment.<br><br>
    However, online learning also presents certain challenges. Without self-discipline, students may easily get distracted by social media or online games during self-study sessions. Educational experts suggest that parents should establish clear study schedules and monitor their children's screen time. Furthermore, combining online self-study with traditional classroom interaction—known as blended learning—remains the most effective strategy for mastering English communication skills.
</div>
"""

# 1. DO TEST MODE
if mode == "📝 Làm bài thi":
    st.info("⏱️ **Thời gian làm bài:** 90 phút | **Tổng số câu:** 40 câu | **Thang điểm:** 10.0 điểm (0.25đ / câu)")

    with st.form("exam_form"):
        st.subheader("👤 Thông tin thí sinh")
        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("Họ và tên học sinh *", placeholder="Ví dụ: Nguyễn Văn An")
        with col2:
            student_info = st.text_input("Lớp / Số điện thoại *", placeholder="Ví dụ: Lớp 9A1 - 0901234567")

        st.markdown("---")
        
        user_responses = {}
        current_part = ""

        for q in QUESTIONS:
            if q["part"] != current_part:
                current_part = q["part"]
                st.markdown(f"<div class='section-header'>{current_part}</div>", unsafe_allow_html=True)

                if "CLOZE TEST" in current_part:
                    st.markdown(CLOZE_PASSAGE, unsafe_allow_html=True)
                elif "READING COMPREHENSION" in current_part:
                    st.markdown(READING_PASSAGE, unsafe_allow_html=True)

            # Display Question Badge
            st.markdown(f"<span class='q-badge'>Câu {q['id']} / 40</span>", unsafe_allow_html=True)
            
            if "notice_html" in q:
                st.markdown(q["notice_html"], unsafe_allow_html=True)

            if q["type"] == "mcq":
                st.markdown(f"**{q['question']}**", unsafe_allow_html=True)
                user_responses[q["id"]] = st.radio(
                    f"Lựa chọn đáp án cho Câu {q['id']}:",
                    options=q["options_display"],
                    index=None,
                    key=f"q_{q['id']}",
                    label_visibility="collapsed"
                )
            else:
                user_responses[q["id"]] = st.text_input(
                    f"**{q['question']}**",
                    key=f"q_{q['id']}",
                    placeholder="Nhập câu trả lời của bạn..."
                )

            st.markdown("<br>", unsafe_allow_html=True)

        submitted = st.form_submit_button("🚀 NỘP BÀI THI & XEM LỜI GIẢI CHI TIẾT", use_container_width=True)

    if submitted:
        if not student_name.strip() or not student_info.strip():
            st.error("⚠️ **Vui lòng điền đầy đủ Họ và tên cùng Lớp/SĐT trước khi nộp bài!**")
        else:
            # Grading
            correct_count = 0
            details = []

            for q in QUESTIONS:
                q_id = q["id"]
                u_ans = user_responses.get(q_id, "")
                is_correct = False

                if q["type"] == "mcq":
                    if u_ans and u_ans.startswith(q["answer"][:2]):
                        is_correct = True
                else:
                    clean_u = (u_ans or "").strip().lower().replace(".", "")
                    clean_accepted = [acc.strip().lower().replace(".", "") for acc in q.get("accepted_answers", [])]
                    if clean_u in clean_accepted:
                        is_correct = True

                if is_correct:
                    correct_count += 1

                details.append({
                    "id": q_id,
                    "question": q["question"],
                    "user_answer": u_ans if u_ans else "(Chưa trả lời)",
                    "correct_answer": q["answer"],
                    "is_correct": is_correct,
                    "explanation": q["explanation"]
                })

            final_score = round((correct_count / len(QUESTIONS)) * 10, 2)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Save to Database
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('''
                INSERT INTO submissions (student_name, student_info, score, max_score, submitted_at, answers_json)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_name, student_info, final_score, 10.0, timestamp, json.dumps(details, ensure_ascii=False)))
            conn.commit()
            conn.close()

            # Display Results
            st.balloons()
            st.success(f"🎉 **Chúc mừng học sinh {student_name} đã hoàn thành bài thi!**")
            
            score_col1, score_col2, score_col3 = st.columns(3)
            score_col1.metric("Kết quả làm bài", f"{correct_count} / 40 câu đúng")
            score_col2.metric("Điểm số tổng kết", f"{final_score} / 10.0 điểm")
            score_col3.metric("Thời điểm nộp bài", timestamp)

            st.markdown("---")
            st.subheader("🔍 Chi tiết Bài làm & Lời giải từng câu")

            for item in details:
                icon = "✅" if item["is_correct"] else "❌"
                status_text = "ĐÚNG (+0.25đ)" if item["is_correct"] else "SAI (0đ)"
                
                with st.expander(f"{icon} Câu {item['id']}: {status_text}"):
                    st.write(f"**Nội dung câu hỏi:** {item['question']}", unsafe_allow_html=True)
                    st.write(f"**Bài làm của bạn:** `{item['user_answer']}`", unsafe_allow_html=True)
                    st.write(f"**Đáp án chính xác:** `{item['correct_answer']}`", unsafe_allow_html=True)
                    st.info(f"💡 **Giải thích đáp án & Bẫy cần lưu ý:**\n\n{item['explanation']}", icon="💡")

# 2. VIEW HISTORY MODE
elif mode == "📜 Lịch sử bài làm":
    st.header("📜 Tra cứu Lịch sử Bài làm Học sinh")
    search_query = st.text_input("🔍 Nhập Họ tên hoặc Lớp / SĐT để tìm kiếm kết quả:", placeholder="Ví dụ: Nguyễn Văn An hoặc 0901234567")

    if search_query.strip():
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query('''
            SELECT id, student_name as 'Họ tên', student_info as 'Lớp/SĐT', score as 'Điểm số', submitted_at as 'Thời gian nộp', answers_json
            FROM submissions
            WHERE student_name LIKE ? OR student_info LIKE ?
            ORDER BY id DESC
        ''', conn, params=(f"%{search_query}%", f"%{search_query}%"))
        conn.close()

        if df.empty:
            st.warning("⚠️ Không tìm thấy kết quả làm bài khớp với thông tin đã nhập.")
        else:
            st.success(f"Tìm thấy {len(df)} lượt làm bài:")
            st.dataframe(df[['Họ tên', 'Lớp/SĐT', 'Điểm số', 'Thời gian nộp']], use_container_width=True)

            selected_id = st.selectbox("Chọn lượt làm bài để mở xem lại chi tiết:", df['id'].tolist())
            if selected_id:
                row = df[df['id'] == selected_id].iloc[0]
                st.subheader(f"📊 Kết quả chi tiết của {row['Họ tên']} — Điểm số: {row['Điểm số']} / 10.0")
                answers = json.loads(row['answers_json'])

                for item in answers:
                    icon = "✅" if item["is_correct"] else "❌"
                    with st.expander(f"{icon} Câu {item['id']}: {'ĐÚNG' if item['is_correct'] else 'SAI'}"):
                        st.write(f"**Nội dung:** {item['question']}", unsafe_allow_html=True)
                        st.write(f"**Bài làm:** `{item['user_answer']}`")
                        st.write(f"**Đáp án đúng:** `{item['correct_answer']}`")
                        st.info(f"💡 **Giải thích:** {item['explanation']}")

# 3. ADMIN DASHBOARD MODE
elif mode == "🔑 Quản trị viên (Admin)":
    st.header("🔑 Bảng Quản trị Giáo viên & Thống kê")
    password = st.text_input("Mật khẩu Quản trị viên:", type="password")

    if password == "admin123":
        st.success("🔓 Đăng nhập Admin thành công!")

        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query('''
            SELECT id as 'Mã bài', student_name as 'Họ và Tên', student_info as 'Lớp / SĐT', score as 'Điểm số (Thang 10)', submitted_at as 'Thời điểm nộp'
            FROM submissions
            ORDER BY id DESC
        ''', conn)
        conn.close()

        if df.empty:
            st.info("Chưa có học sinh nào nộp bài trên hệ thống.")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Tổng số bài nộp", len(df))
            c2.metric("Điểm trung bình", f"{df['Điểm số (Thang 10)'].mean():.2f}")
            c3.metric("Điểm cao nhất", f"{df['Điểm số (Thang 10)'].max():.2f}")
            c4.metric("Điểm thấp nhất", f"{df['Điểm số (Thang 10)'].min():.2f}")

            st.markdown("---")
            st.subheader("📋 Bảng tổng hợp toàn bộ học sinh đã làm bài")
            st.dataframe(df, use_container_width=True)

            # CSV Download
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Tải Báo cáo Danh sách & Điểm số (File CSV/Excel)",
                data=csv_data,
                file_name=f"Bao_cao_diem_thi_anh9_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    elif password != "":
        st.error("⚠️ Mật khẩu Quản trị viên không chính xác!")
