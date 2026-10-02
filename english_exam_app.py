import sqlite3
import json
import os
import pandas as pd
import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Hệ thống Chấm bài Thi Tuyển sinh 10 Tiếng Anh - TP.HCM",
    page_icon="📝",
    layout="wide"
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

# Questions Data
QUESTIONS = [
    # I. MULTIPLE CHOICE
    {"id": 1, "type": "mcq", "part": "I. MULTIPLE CHOICE (Pronunciation & Stress)",
     "question": "Choose the word whose underlined part differs from the other three in pronunciation:",
     "options": ["A. missed", "B. lived", "C. cooked", "D. stopped"],
     "answer": "B. lived",
     "explanation": "'lived' phát âm là /d/; các từ còn lại phát âm là /t/ (/mɪst/, /kʊkt/, /stɒpt/)."},
    
    {"id": 2, "type": "mcq", "part": "I. MULTIPLE CHOICE (Pronunciation & Stress)",
     "question": "Choose the word whose underlined part differs from the other three in pronunciation:",
     "options": ["A. climate", "B. litter", "C. village", "D. habit"],
     "answer": "A. climate",
     "explanation": "'climate' phát âm là /aɪ/ (/ˈklaɪ.mət/); các từ còn lại là /ɪ/ (/ˈlɪt.ər/, /ˈvɪl.ɪdʒ/, /ˈhæb.ɪt/)."},
    
    {"id": 3, "type": "mcq", "part": "I. MULTIPLE CHOICE (Pronunciation & Stress)",
     "question": "Choose the word that differs from the other three in the position of primary stress:",
     "options": ["A. reduce", "B. suggest", "C. offer", "D. protect"],
     "answer": "C. offer",
     "explanation": "'offer' có trọng âm rơi vào âm tiết 1 (/ˈɒf.ər/); các từ còn lại trọng âm 2."},
    
    {"id": 4, "type": "mcq", "part": "I. MULTIPLE CHOICE (Pronunciation & Stress)",
     "question": "Choose the word that differs from the other three in the position of primary stress:",
     "options": ["A. decision", "B. pollution", "C. energy", "D. official"],
     "answer": "C. energy",
     "explanation": "'energy' có trọng âm rơi vào âm tiết 1 (/ˈen.ə.dʒi/); các từ còn lại trọng âm 2."},

    {"id": 5, "type": "mcq", "part": "I. MULTIPLE CHOICE (Grammar & Vocabulary)",
     "question": "Linh recently moved to a busy district in Ho Chi Minh City. She finds it hard to sleep because she is not used ______ to the constant noise of vehicles at night.",
     "options": ["A. to listen", "B. to listening", "C. for listening", "D. listen"],
     "answer": "B. to listening",
     "explanation": "Cấu trúc 'be used to + V-ing/Noun' diễn tả sự quen thuộc với việc gì ở hiện tại."},

    {"id": 6, "type": "mcq", "part": "I. MULTIPLE CHOICE (Grammar & Vocabulary)",
     "question": "During the job interview at a tech company in District 1, the manager asked Minh ______ in digital marketing before applying for this position.",
     "options": ["A. how many years of experience had he got", "B. how many years of experience he had got", "C. if had he got experience", "D. that he had got any experience"],
     "answer": "B. how many years of experience he had got",
     "explanation": "Trong câu tường thuật (Reported Speech), mệnh đề câu hỏi Wh-question giữ trật tự xuôi S + V, không đảo trợ động từ."},

    {"id": 7, "type": "mcq", "part": "I. MULTIPLE CHOICE (Grammar & Vocabulary)",
     "question": "You should bring an umbrella with you ______ it rains heavily during our eco-tour in Can Gio mangrove forest this afternoon.",
     "options": ["A. if", "B. in case", "C. unless", "D. provided"],
     "answer": "B. in case",
     "explanation": "'In case' (phòng khi) dùng chỉ hành động chuẩn bị/phòng ngừa trước một khả năng xảy ra."},

    {"id": 8, "type": "mcq", "part": "I. MULTIPLE CHOICE (Grammar & Vocabulary)",
     "question": "I have so much revision to finish for the upcoming exam. I wish I ______ join my classmates for the charity fair in the school yard today.",
     "options": ["A. would", "B. could", "C. can", "D. will"],
     "answer": "B. could",
     "explanation": "Câu ước ở hiện tại với bản thân (I wish I) dùng 'could + V0', không dùng 'would'."},

    {"id": 9, "type": "mcq", "part": "I. MULTIPLE CHOICE (Grammar & Vocabulary)",
     "question": "______ the severe traffic congestion on Cong Hoa Street during peak hours, the express bus arrived at the station right on time.",
     "options": ["A. Although", "B. In spite", "C. Despite of", "D. In spite of"],
     "answer": "D. In spite of",
     "explanation": "'In spite of + Noun Phrase'. 'Despite' không đi với 'of' (Đáp án C sai grammar)."},

    {"id": 10, "type": "mcq", "part": "I. MULTIPLE CHOICE (Grammar & Vocabulary)",
     "question": "Many rare species of birds ______ to have returned to the Dong Nai Nature Reserve after recent reforestation efforts.",
     "options": ["A. report", "B. are reported", "C. are reporting", "D. have reported"],
     "answer": "B. are reported",
     "explanation": "Cấu trúc bị động với động từ chỉ ý kiến/báo cáo: S + be + V3 + to-V."},

    {"id": 11, "type": "mcq", "part": "I. MULTIPLE CHOICE (Grammar & Vocabulary)",
     "question": "The school STEM project was ______ a great success that all visitors expressed their admiration for the young inventors.",
     "options": ["A. so", "B. such", "C. too", "D. enough"],
     "answer": "B. such",
     "explanation": "Cấu trúc: 'such + a/an + Adj + Noun + that'."},

    {"id": 12, "type": "mcq", "part": "I. MULTIPLE CHOICE (Communication)",
     "question": "Nam: 'Why don't we bring reusable thermos flasks to school every day?' - Mai: '______ That will significantly cut down on single-use plastic cups.'",
     "options": ["A. You're welcome.", "B. I couldn't agree more!", "C. Never mind.", "D. It's my pleasure."],
     "answer": "B. I couldn't agree more!",
     "explanation": "'I couldn't agree more!' thể hiện sự đồng ý hoàn toàn với ý kiến đề xuất."},

    {"id": 13, "type": "mcq", "part": "I. MULTIPLE CHOICE (Signs & Notices)",
     "question": "Look at the notice: 'NOTICE: LIBRARY QUIET ZONE - Please turn off your mobile phones or switch them to silent mode before entering the room.' What does it tell you?",
     "options": [
         "A. Mobile phones are completely forbidden inside the library.",
         "B. Visitors must ensure their phones do not make noise in this area.",
         "C. You are allowed to make phone calls if you speak in a low voice.",
         "D. All electronic devices must be handed over to the librarian."
     ],
     "answer": "B. Visitors must ensure their phones do not make noise in this area.",
     "explanation": "Thông báo yêu cầu người vào thư viện đảm bảo điện thoại không phát ra tiếng động (tắt máy hoặc để im lặng)."},

    {"id": 14, "type": "mcq", "part": "I. MULTIPLE CHOICE (Signs & Notices)",
     "question": "Look at the warning sign: 'WARNING: SLIPPERY SURFACE WHEN WET - Please watch your step!' What does it mean?",
     "options": [
         "A. The floor is currently dry and safe for running.",
         "B. People should walk carefully because the surface can cause slips when wet.",
         "C. Water is strictly prohibited in this corridor.",
         "D. Pedestrians must wear special boots before stepping here."
     ],
     "answer": "B. People should walk carefully because the surface can cause slips when wet.",
     "explanation": "Cảnh báo sàn trơn trượt khi ướt, cần chú ý bước đi cẩn thận."},

    # II. CLOZE TEST
    {"id": 15, "type": "mcq", "part": "II. CLOZE TEST (Green Lifestyles)",
     "question": "In recent years, many young citizens in Ho Chi Minh City have started adopting greener lifestyles to protect the environment. They realize that small daily actions can lead to positive environmental impacts. (15) ______, many students now choose to commute by public electric buses or bicycles instead of personal motorbikes.",
     "options": ["A. However", "B. For instance", "C. Therefore", "D. Otherwise"],
     "answer": "B. For instance",
     "explanation": "'For instance' (Ví dụ như) đưa ra ví dụ cụ thể cho ý 'hành động nhỏ hàng ngày' ở câu trước."},

    {"id": 16, "type": "mcq", "part": "II. CLOZE TEST (Green Lifestyles)",
     "question": "Additionally, teenagers are becoming more conscious of single-use plastic waste. Instead of buying disposable bottles, they carry personal water containers. Many coffee shops in the city also encourage this trend (16) ______ offering discounts to customers who bring their own cups.",
     "options": ["A. by", "B. for", "C. with", "D. on"],
     "answer": "A. by",
     "explanation": "Cấu trúc 'by + V-ing' dùng để chỉ phương thức/cách thức thực hiện hành động."},

    {"id": 17, "type": "mcq", "part": "II. CLOZE TEST (Green Lifestyles)",
     "question": "Community groups regularly organize weekend clean-up campaigns along local canals. (17) ______ the hot weather, hundreds of volunteers gather enthusiastically to collect garbage and sort recyclable materials.",
     "options": ["A. Although", "B. Because of", "C. In spite of", "D. Because"],
     "answer": "C. In spite of",
     "explanation": "'In spite of + Noun Phrase' (In spite of the hot weather) thể hiện sự nhượng bộ."},

    {"id": 18, "type": "mcq", "part": "II. CLOZE TEST (Green Lifestyles)",
     "question": "A high school student participating in last Sunday's event shared that if more citizens (18) ______ part in such community activities, the city would become much cleaner and more liveable.",
     "options": ["A. take", "B. took", "C. had taken", "D. will take"],
     "answer": "B. took",
     "explanation": "Câu điều kiện loại 2 giả định ở hiện tại (Mệnh đề If dùng V2/ed: 'took')."},

    {"id": 19, "type": "mcq", "part": "II. CLOZE TEST (Green Lifestyles)",
     "question": "Furthermore, local authorities are planning to install smart recycling bins in major parks to educate the public (19) ______ waste separation at source.",
     "options": ["A. about", "B. for", "C. with", "D. in"],
     "answer": "A. about",
     "explanation": "Cụm từ 'educate somebody about something' (giáo dục ai về điều gì)."},

    {"id": 20, "type": "mcq", "part": "II. CLOZE TEST (Green Lifestyles)",
     "question": "It is hoped that every resident will soon get used to (20) ______ green habits as a normal part of their daily routine.",
     "options": ["A. practice", "B. practicing", "C. practiced", "D. to practice"],
     "answer": "B. practicing",
     "explanation": "Cấu trúc 'get used to + V-ing' (dần quen với việc làm gì)."},

    # III. READING COMPREHENSION
    {"id": 21, "type": "mcq", "part": "III. READING COMPREHENSION (Digital English Learning)",
     "question": "Statement 21: 'Online learning platforms have become vital resources for entrance exam preparation in Vietnam.' - Is this statement True or False according to the passage?",
     "options": ["True", "False"],
     "answer": "True",
     "explanation": "Trích bài: 'Online learning platforms and digital resource libraries have become essential tools for both teachers and students preparing for important entrance examinations.'"},

    {"id": 22, "type": "mcq", "part": "III. READING COMPREHENSION (Digital English Learning)",
     "question": "Statement 22: 'Automated feedback systems force students to wait several days to identify their test errors.' - Is this statement True or False according to the passage?",
     "options": ["True", "False"],
     "answer": "False",
     "explanation": "Trích bài: 'automated feedback systems allow students to identify their mistakes immediately...' (Phản hồi tức thì chứ không phải chờ vài ngày)."},

    {"id": 23, "type": "mcq", "part": "III. READING COMPREHENSION (Digital English Learning)",
     "question": "Statement 23: 'Social media distraction is one of the obstacles students face during online self-study.' - Is this statement True or False according to the passage?",
     "options": ["True", "False"],
     "answer": "True",
     "explanation": "Trích bài: 'Without self-discipline, students may easily get distracted by social media or online games...'"},

    {"id": 24, "type": "mcq", "part": "III. READING COMPREHENSION (Digital English Learning)",
     "question": "Statement 24: 'Educational experts advise against combining online learning with traditional classroom instruction.' - Is this statement True or False according to the passage?",
     "options": ["True", "False"],
     "answer": "False",
     "explanation": "Trích bài: 'combining online self-study with traditional classroom interaction... remains the most effective strategy...' (Chuyên gia khuyến khích chứ không khuyên chống lại)."},

    {"id": 25, "type": "mcq", "part": "III. READING COMPREHENSION (Digital English Learning)",
     "question": "Question 25: The word 'flexibility' in paragraph 2 is closest in meaning to:",
     "options": ["A. difficulty", "B. adaptability", "C. strictness", "D. weakness"],
     "answer": "B. adaptability",
     "explanation": "'flexibility' có nghĩa là tính linh hoạt, khả năng thích ứng (adaptability)."},

    {"id": 26, "type": "mcq", "part": "III. READING COMPREHENSION (Digital English Learning)",
     "question": "Question 26: What is the main idea of the passage?",
     "options": [
         "A. The history of printed textbooks in Vietnamese secondary schools.",
         "B. The benefits and challenges of digital English learning for students.",
         "C. Why students should completely replace classroom learning with smartphones.",
         "D. How parents can teach English grammar to their children at home."
     ],
     "answer": "B. The benefits and challenges of digital English learning for students.",
     "explanation": "Nội dung bao quát toàn bài trình bày cả lợi ích (Đoạn 2) và thách thức (Đoạn 3) của việc học tiếng Anh trực tuyến."},

    # IV. WORD FORMATION
    {"id": 27, "type": "text", "part": "IV. WORD FORMATION",
     "question": "Question 27: The school board decided to ____________ the main gate road to avoid traffic jams during peak hours. (WIDE)",
     "answer": "widen",
     "accepted_answers": ["widen"],
     "explanation": "Cần một động từ sau 'decided to': 'widen' (mở rộng con đường)."},

    {"id": 28, "type": "text", "part": "IV. WORD FORMATION",
     "question": "Question 28: Environmentalists are deeply concerned about the severe ____________ of air quality in industrial zones. (POLLUTE)",
     "answer": "pollution",
     "accepted_answers": ["pollution"],
     "explanation": "Cần danh từ đứng sau tính từ 'severe': 'pollution' (sự ô nhiễm)."},

    {"id": 29, "type": "text", "part": "IV. WORD FORMATION",
     "question": "Question 29: The tour guide gave a very ____________ explanation about the historic architecture of the Saigon Central Post Office. (INFORM)",
     "answer": "informative",
     "accepted_answers": ["informative"],
     "explanation": "Cần tính từ đứng trước danh từ 'explanation': 'informative' (nhiều thông tin/bổ ích)."},

    {"id": 30, "type": "text", "part": "IV. WORD FORMATION",
     "question": "Question 30: Thousands of high school volunteers ____________ participated in the city's green campaign last Sunday. (ENTHUSIASTIC)",
     "answer": "enthusiastically",
     "accepted_answers": ["enthusiastically"],
     "explanation": "Cần trạng từ bổ nghĩa cho động từ 'participated': 'enthusiastically' (một cách hào hứng)."},

    {"id": 31, "type": "text", "part": "IV. WORD FORMATION",
     "question": "Question 31: Regular physical exercise and a balanced diet are key factors to improve your overall health and ____________. (STRONG)",
     "answer": "strength",
     "accepted_answers": ["strength"],
     "explanation": "Cần danh từ sau 'health and': 'strength' (sức mạnh/thể lực)."},

    {"id": 32, "type": "text", "part": "IV. WORD FORMATION",
     "question": "Question 32: It is ____________ to ride motorbikes on the pedestrian pavement, and violators will be heavily fined. (LEGAL)",
     "answer": "illegal",
     "accepted_answers": ["illegal"],
     "explanation": "Cần tính từ phủ định: 'illegal' (bất hợp pháp / trái pháp luật)."},

    # V. SENTENCE REARRANGEMENT
    {"id": 33, "type": "text", "part": "V. SENTENCE REARRANGEMENT",
     "question": "Question 33: Rearrange the group of words: 'Students should / in order to / bring reusable water bottles / single-use plastic waste / reduce / .'\nStarts with: Students...",
     "answer": "Students should bring reusable water bottles in order to reduce single-use plastic waste.",
     "accepted_answers": [
         "students should bring reusable water bottles in order to reduce single-use plastic waste.",
         "students should bring reusable water bottles in order to reduce single-use plastic waste"
     ],
     "explanation": "Cấu trúc chỉ mục đích: S + should + V0 + in order to + V0."},

    {"id": 34, "type": "text", "part": "V. SENTENCE REARRANGEMENT",
     "question": "Question 34: Rearrange the group of words: 'save energy / If everyone / turns off unnecessary lights / protect the environment / , / we can / and / .'\nStarts with: If everyone...",
     "answer": "If everyone turns off unnecessary lights, we can save energy and protect the environment.",
     "accepted_answers": [
         "if everyone turns off unnecessary lights, we can save energy and protect the environment.",
         "if everyone turns off unnecessary lights, we can save energy and protect the environment"
     ],
     "explanation": "Câu điều kiện loại 1 diễn tả khả năng thực tế ở hiện tại/tương lai."},

    # VI. SENTENCE TRANSFORMATION
    {"id": 35, "type": "text", "part": "VI. SENTENCE TRANSFORMATION",
     "question": "Question 35: I am sorry that I cannot attend your English speaking club meeting this Saturday.\nRewrite: I wish...",
     "answer": "I wish I could attend your English speaking club meeting this Saturday.",
     "accepted_answers": [
         "i wish i could attend your english speaking club meeting this saturday.",
         "i wish i could attend your english speaking club meeting this saturday"
     ],
     "explanation": "Ước cho hiện tại/tương lai dùng 'wish + S + could + V0'."},

    {"id": 36, "type": "text", "part": "VI. SENTENCE TRANSFORMATION",
     "question": "Question 36: Lan doesn't have a personal laptop, so she cannot join the online group discussion tonight.\nRewrite: If Lan...",
     "answer": "If Lan had a personal laptop, she could join the online group discussion tonight.",
     "accepted_answers": [
         "if lan had a personal laptop, she could join the online group discussion tonight.",
         "if lan had a personal laptop, she could join the online group discussion tonight"
     ],
     "explanation": "Giả định trái thực tế ở hiện tại dùng Câu điều kiện loại 2: If + S + V2/ed, S + could + V0."},

    {"id": 37, "type": "text", "part": "VI. SENTENCE TRANSFORMATION",
     "question": "Question 37: 'If I were you, I would spend more time practicing listening comprehension,' Mr. Tuan said to Minh.\nRewrite: Mr. Tuan advised...",
     "answer": "Mr. Tuan advised Minh to spend more time practicing listening comprehension.",
     "accepted_answers": [
         "mr. tuan advised minh to spend more time practicing listening comprehension.",
         "mr. tuan advised minh to spend more time practicing listening comprehension"
     ],
     "explanation": "Chuyển câu lời khuyên 'If I were you...' sang dạng gián tiếp: 'advised + O + to-V'."},

    {"id": 38, "type": "text", "part": "VI. SENTENCE TRANSFORMATION",
     "question": "Question 38: A professional technician repaired my father's air conditioner yesterday afternoon.\nRewrite: My father had...",
     "answer": "My father had his air conditioner repaired by a professional technician yesterday afternoon.",
     "accepted_answers": [
         "my father had his air conditioner repaired by a professional technician yesterday afternoon.",
         "my father had his air conditioner repaired by a professional technician yesterday afternoon"
     ],
     "explanation": "Cấu trúc bị động truyền sai: 'have + something + V3/ed + (by O)'."},

    {"id": 39, "type": "text", "part": "VI. SENTENCE TRANSFORMATION",
     "question": "Question 39: Although the weather was extremely rainy, the outdoor music concert was not cancelled.\nRewrite: In spite of...",
     "answer": "In spite of the extremely rainy weather, the outdoor music concert was not cancelled.",
     "accepted_answers": [
         "in spite of the extremely rainy weather, the outdoor music concert was not cancelled.",
         "in spite of the extremely rainy weather, the outdoor music concert was not cancelled",
         "in spite of the fact that the weather was extremely rainy, the outdoor music concert was not cancelled.",
         "in spite of the fact that the weather was extremely rainy, the outdoor music concert was not cancelled"
     ],
     "explanation": "Chuyển từ mệnh đề 'Although + S + be + Adj' sang cụm danh từ 'In spite of + Noun Phrase'."},

    {"id": 40, "type": "text", "part": "VI. SENTENCE TRANSFORMATION",
     "question": "Question 40: The suitcase was so heavy that the young boy couldn't lift it onto the luggage rack.\nRewrite: The suitcase was too...",
     "answer": "The suitcase was too heavy for the young boy to lift onto the luggage rack.",
     "accepted_answers": [
         "the suitcase was too heavy for the young boy to lift onto the luggage rack.",
         "the suitcase was too heavy for the young boy to lift onto the luggage rack"
     ],
     "explanation": "Chuyển từ 'so...that' sang 'too...to': 'too + Adj + for O + to-V' (Lưu ý bắt buộc bỏ tân ngữ 'it' ở cuối câu)."}
]

# Sidebar Navigation
st.sidebar.title("📌 Điều hướng")
mode = st.sidebar.radio("Chọn chức năng:", ["📝 Làm bài thi", "📜 Lịch sử bài làm", "🔑 Quản trị viên (Admin)"])

# 1. DO TEST
if mode == "📝 Làm bài thi":
    st.header("📝 Đề thi thử Tuyển sinh 10 Tiếng Anh - TP.HCM (2026 - 2027)")
    st.caption("Thời gian làm bài: 90 phút | Tổng số câu: 40 câu | Thang điểm: 10.0")

    with st.form("exam_form"):
        st.subheader("👤 Thông tin học sinh")
        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("Họ và tên học sinh *", placeholder="Nguyễn Văn A")
        with col2:
            student_info = st.text_input("Lớp / Số điện thoại *", placeholder="Lớp 9A1 - 0901234567")

        st.markdown("---")
        
        user_responses = {}
        current_part = ""

        for q in QUESTIONS:
            if q["part"] != current_part:
                current_part = q["part"]
                st.markdown(f"### {current_part}")

            if q["type"] == "mcq":
                user_responses[q["id"]] = st.radio(
                    f"**Câu {q['id']}:** {q['question']}",
                    options=q["options"],
                    index=None,
                    key=f"q_{q['id']}"
                )
            else:
                user_responses[q["id"]] = st.text_input(
                    f"**Câu {q['id']}:** {q['question']}",
                    key=f"q_{q['id']}"
                )

        submitted = st.form_submit_button("🚀 Nộp bài & Xem kết quả")

    if submitted:
        if not student_name.strip() or not student_info.strip():
            st.error("⚠️ Vui lòng điền đầy đủ Họ và tên cùng Lớp/SĐT trước khi nộp bài!")
        else:
            # Grading
            correct_count = 0
            details = []

            for q in QUESTIONS:
                q_id = q["id"]
                u_ans = user_responses.get(q_id, "")
                is_correct = False

                if q["type"] == "mcq":
                    if u_ans == q["answer"]:
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
            st.success(f"🎉 Chúc mừng **{student_name}** đã hoàn thành bài thi!")
            
            score_col1, score_col2, score_col3 = st.columns(3)
            score_col1.metric("Số câu đúng", f"{correct_count} / {len(QUESTIONS)}")
            score_col2.metric("Điểm số", f"{final_score} / 10.0")
            score_col3.metric("Thời gian nộp", timestamp)

            st.markdown("---")
            st.subheader("🔍 Bảng đáp án & Lời giải chi tiết")

            for item in details:
                icon = "✅" if item["is_correct"] else "❌"
                with st.expander(f"{icon} Câu {item['id']}: {'ĐÚNG' if item['is_correct'] else 'SAI'}"):
                    st.write(f"**Câu hỏi:** {item['question']}")
                    st.write(f"**Câu trả lời của học sinh:** `{item['user_answer']}`")
                    st.write(f"**Đáp án đúng chuẩn:** `{item['correct_answer']}`")
                    st.info(f"💡 **Lời giải chi tiết:** {item['explanation']}")

# 2. VIEW HISTORY
elif mode == "📜 Lịch sử bài làm":
    st.header("📜 Trắc cứu Lịch sử Làm bài")
    search_query = st.text_input("Nhập Họ tên hoặc Lớp / Số điện thoại để tìm kiếm:", placeholder="Ví dụ: Nguyễn Văn A hoặc 0901234567")

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
            st.warning("Không tìm thấy lịch sử làm bài khớp với thông tin đã nhập.")
        else:
            st.dataframe(df[['Họ tên', 'Lớp/SĐT', 'Điểm số', 'Thời gian nộp']], use_container_width=True)

            selected_id = st.selectbox("Chọn lượt làm bài để xem chi tiết bài giải:", df['id'].tolist())
            if selected_id:
                row = df[df['id'] == selected_id].iloc[0]
                st.subheader(f"Chi tiết bài làm của {row['Họ tên']} - Điểm: {row['Điểm số']}/10.0")
                answers = json.loads(row['answers_json'])

                for item in answers:
                    icon = "✅" if item["is_correct"] else "❌"
                    with st.expander(f"{icon} Câu {item['id']}: {item['question']}"):
                        st.write(f"**Bài làm:** `{item['user_answer']}`")
                        st.write(f"**Đáp án đúng:** `{item['correct_answer']}`")
                        st.info(f"💡 **Giải thích:** {item['explanation']}")

# 3. ADMIN DASHBOARD
elif mode == "🔑 Quản trị viên (Admin)":
    st.header("🔑 Bảng Điều hành Quản trị viên (Admin Dashboard)")
    password = st.text_input("Mật khẩu Quản trị viên:", type="password")

    if password == "admin123":
        st.success("Xác thực thành công! Đang tải dữ liệu toàn bộ bài làm...")

        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query('''
            SELECT id, student_name as 'Họ và Tên', student_info as 'Lớp / SĐT', score as 'Điểm số (Thang 10)', submitted_at as 'Thời điểm nộp bài'
            FROM submissions
            ORDER BY id DESC
        ''', conn)
        conn.close()

        if df.empty:
            st.info("Chưa có lượt nộp bài nào trên hệ thống.")
        else:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Tổng số bài nộp", len(df))
            col2.metric("Điểm trung bình", f"{df['Điểm số (Thang 10)'].mean():.2f}")
            col3.metric("Điểm cao nhất", df['Điểm số (Thang 10)'].max())
            col4.metric("Điểm thấp nhất", df['Điểm số (Thang 10)'].min())

            st.markdown("---")
            st.subheader("📊 Danh sách chi tiết học sinh đã nộp bài")
            st.dataframe(df, use_container_width=True)

            # CSV Download
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Tải Báo cáo Danh sách & Điểm số (File CSV/Excel)",
                data=csv_data,
                file_name=f"Danh_sach_diem_thi_anh9_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

    elif password != "":
        st.error("Mật khẩu Quản trị viên không chính xác!")
