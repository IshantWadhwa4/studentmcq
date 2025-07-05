import streamlit as st
import json
import requests
import base64
import time
from datetime import datetime, timedelta
import os

# GitHub configuration
GITHUB_REPO = "IshantWadhwa4/data_tsmcq"
GITHUB_PATH = "questions"  # Path where test files are stored
RESULTS_PATH = "students_solution"  # Path where student results will be stored

def load_test_from_github(test_id, student_token):
    """Load test data from GitHub repository"""
    try:
        # GitHub API endpoint
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{test_id}.json"
        
        # Headers
        headers = {
            "Authorization": f"token {student_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Make the request
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            file_data = response.json()
            content = base64.b64decode(file_data['content']).decode()
            test_data = json.loads(content)
            return True, test_data
        else:
            return False, f"Test not found: {response.status_code}"
    
    except Exception as e:
        return False, f"Error loading test: {str(e)}"

def save_student_result_to_github(result_data, student_name, test_id, student_token):
    """Save student result to GitHub repository"""
    try:
        # Create filename with timestamp
        timestamp = int(time.time())
        filename = f"{student_name}_{test_id}_{timestamp}.json"
        
        # GitHub API endpoint
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{RESULTS_PATH}/{filename}"
        
        # Prepare the content
        content = json.dumps(result_data, indent=2)
        encoded_content = base64.b64encode(content.encode()).decode()
        
        # API request data
        data = {
            "message": f"Add student result: {student_name} - {test_id}",
            "content": encoded_content,
            "branch": "main"  # or your default branch
        }
        
        # Headers
        headers = {
            "Authorization": f"token {student_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Make the request
        response = requests.put(url, json=data, headers=headers)
        
        if response.status_code == 201:
            return True, "Results successfully saved to GitHub"
        else:
            return False, f"Error saving results: {response.status_code} - {response.text}"
    
    except Exception as e:
        return False, f"Error saving results: {str(e)}"

def display_question(question, question_num, total_questions):
    """Display a single question with options"""
    st.markdown(f"### Question {question_num} of {total_questions}")
    st.write(question['question_text'])
    
    # Display options
    option_key = f"q_{question_num}"
    selected_answer = st.radio(
        "Choose your answer:",
        options=list(question['options'].keys()),
        format_func=lambda x: f"{x}. {question['options'][x]}",
        key=option_key
    )
    
    return selected_answer

def calculate_score(questions, student_answers):
    """Calculate score and generate results"""
    total_questions = len(questions)
    correct_answers = 0
    results = []
    
    for i, question in enumerate(questions):
        question_num = i + 1
        student_answer = student_answers.get(f"q_{question_num}")
        correct_answer = question['correct_answer']
        is_correct = student_answer == correct_answer
        
        if is_correct:
            correct_answers += 1
        
        result = {
            "question_number": question_num,
            "question_text": question['question_text'],
            "options": question['options'],
            "student_answer": student_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": question.get('explanation', 'No explanation provided'),
            "topic": question.get('topic', 'General'),
            "subtopic": question.get('subtopic', 'N/A'),
            "difficulty": question.get('difficulty', 'Medium')
        }
        results.append(result)
    
    score_percentage = (correct_answers / total_questions) * 100
    
    return {
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "score_percentage": score_percentage,
        "results": results
    }

def display_results(score_data):
    """Display test results with explanations"""
    st.header("📊 Test Results")
    
    # Score summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{score_data['score_percentage']:.1f}%")
    with col2:
        st.metric("Correct", f"{score_data['correct_answers']}/{score_data['total_questions']}")
    with col3:
        st.metric("Incorrect", f"{score_data['total_questions'] - score_data['correct_answers']}")
    
    # Performance indicator
    if score_data['score_percentage'] >= 80:
        st.success("🎉 Excellent performance! Keep up the great work!")
    elif score_data['score_percentage'] >= 60:
        st.info("👍 Good job! There's room for improvement.")
    else:
        st.warning("📚 Keep studying! You can do better next time.")
    
    # Detailed results
    st.header("📋 Detailed Results")
    
    for result in score_data['results']:
        if result['is_correct']:
            st.success(f"✅ Question {result['question_number']}: Correct")
        else:
            st.error(f"❌ Question {result['question_number']}: Incorrect")
        
        with st.expander(f"View Question {result['question_number']} Details"):
            st.write(f"**Question:** {result['question_text']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Options:**")
                for opt_key, opt_text in result['options'].items():
                    if opt_key == result['correct_answer']:
                        st.write(f"✅ **{opt_key}.** {opt_text}")
                    elif opt_key == result['student_answer']:
                        st.write(f"❌ **{opt_key}.** {opt_text} (Your Answer)")
                    else:
                        st.write(f"   **{opt_key}.** {opt_text}")
            
            with col2:
                st.write(f"**Your Answer:** {result['student_answer'] or 'Not answered'}")
                st.write(f"**Correct Answer:** {result['correct_answer']}")
                st.write(f"**Topic:** {result['topic']}")
                st.write(f"**Difficulty:** {result['difficulty']}")
            
            st.write(f"**Explanation:** {result['explanation']}")

def main():
    st.set_page_config(
        page_title="Student MCQ Test",
        page_icon="👨‍🎓",
        layout="wide"
    )
    
    st.title("👨‍🎓 Student MCQ Test")
    st.markdown("Take your MCQ test and get instant results with detailed explanations")
    
    # Initialize session state
    if 'test_loaded' not in st.session_state:
        st.session_state.test_loaded = False
    if 'test_data' not in st.session_state:
        st.session_state.test_data = None
    if 'student_info' not in st.session_state:
        st.session_state.student_info = None
    if 'test_completed' not in st.session_state:
        st.session_state.test_completed = False
    if 'test_started' not in st.session_state:
        st.session_state.test_started = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    
    # Student information and test loading
    if not st.session_state.test_loaded:
        st.header("📝 Student Information")
        
        with st.form("student_form"):
            col1, col2 = st.columns(2)
            with col1:
                student_name = st.text_input("Student Name*", help="Enter your full name")
                email = st.text_input("Email (Optional)", help="Enter your email address")
            with col2:
                student_id = st.text_input("Student ID (Optional)", help="Enter your student ID")
                test_id = st.text_input("Test ID*", help="Enter the Test ID provided by your teacher (e.g., AMIT_20250105_33)")
            
            # Student Token (GitHub Token)
            student_token = st.text_input(
                "Student Token*",
                type="password",
                help="Enter your GitHub Personal Access Token"
            )
            
            submit_button = st.form_submit_button("📖 Load Test", type="primary")
            
            if submit_button:
                if not student_name or not test_id or not student_token:
                    st.error("Please fill in all required fields (marked with *)")
                else:
                    # Load test
                    with st.spinner("Loading test..."):
                        success, test_data = load_test_from_github(test_id, student_token)
                        
                        if success:
                            st.session_state.test_loaded = True
                            st.session_state.test_data = test_data
                            st.session_state.student_info = {
                                "name": student_name,
                                "email": email,
                                "student_id": student_id,
                                "test_id": test_id,
                                "student_token": student_token
                            }
                            st.success("✅ Test loaded successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to load test: {test_data}")
    
    # Display test
    elif st.session_state.test_loaded and not st.session_state.test_completed:
        test_data = st.session_state.test_data
        student_info = st.session_state.student_info
        
        # Test header with teacher information
        st.header(f"📖 {test_data['subject']} Test")
        
        # Display teacher and test information
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.info(f"**Teacher:** {test_data.get('teacher_name', 'Unknown')}")
        with col2:
            st.info(f"**Subject:** {test_data['subject']}")
        with col3:
            st.info(f"**Questions:** {len(test_data['questions'])}")
        with col4:
            st.info(f"**Difficulty:** {test_data['difficulty']}")
        with col5:
            exam_duration = test_data.get('exam_duration_minutes', 60)
            if exam_duration >= 60:
                hours = exam_duration // 60
                mins = exam_duration % 60
                if mins > 0:
                    duration_text = f"{hours}h {mins}m"
                else:
                    duration_text = f"{hours}h"
            else:
                duration_text = f"{exam_duration}m"
            st.info(f"**Duration:** {duration_text}")
        
        if test_data.get('topics'):
            st.info(f"**Topics:** {', '.join(test_data['topics'])}")
        
        # Display test creation date
        if test_data.get('created_at'):
            try:
                created_date = datetime.fromisoformat(test_data['created_at'].replace('Z', '+00:00'))
                st.info(f"**Created:** {created_date.strftime('%Y-%m-%d %H:%M')}")
            except:
                st.info(f"**Created:** {test_data['created_at']}")
        
        # Start Test Button or Timer Display
        if not st.session_state.test_started:
            st.markdown("---")
            st.markdown("### 🚀 Ready to Start?")
            st.markdown(f"⏰ **Time Limit:** {duration_text}")
            st.warning("⚠️ Once you start the test, the timer will begin and cannot be paused!")
            
            if st.button("▶️ Start Test", type="primary", help="Click to start the timed test"):
                st.session_state.test_started = True
                st.session_state.start_time = datetime.now()
                st.rerun()
        else:
            # Calculate remaining time
            exam_duration_minutes = test_data.get('exam_duration_minutes', 60)
            elapsed_time = datetime.now() - st.session_state.start_time
            remaining_time = timedelta(minutes=exam_duration_minutes) - elapsed_time
            
            # Timer display
            if remaining_time.total_seconds() > 0:
                hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                
                # Color coding for timer
                if remaining_time.total_seconds() > 600:  # More than 10 minutes
                    timer_color = "green"
                    timer_bg = "#d4edda"
                    timer_border = "#c3e6cb"
                elif remaining_time.total_seconds() > 300:  # More than 5 minutes
                    timer_color = "orange"
                    timer_bg = "#fff3cd"
                    timer_border = "#ffeaa7"
                else:  # Less than 5 minutes
                    timer_color = "red"
                    timer_bg = "#f8d7da"
                    timer_border = "#f5c6cb"
                
                # Main timer display
                st.markdown("---")
                col_timer1, col_timer2, col_timer3 = st.columns([1, 2, 1])
                with col_timer2:
                    st.markdown(f"### ⏰ Time Remaining: {hours:02d}:{minutes:02d}:{seconds:02d}")
                    st.caption("Timer updates automatically every second. Scroll down to see sticky timer.")
                
                # Sticky timer on the right side
                st.markdown(
                    f"""
                    <div style="
                        position: fixed;
                        top: 100px;
                        right: 20px;
                        background-color: {timer_bg};
                        border: 2px solid {timer_border};
                        border-radius: 10px;
                        padding: 15px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                        z-index: 999;
                        font-family: 'Courier New', monospace;
                        text-align: center;
                        min-width: 150px;
                    ">
                        <div style="
                            font-size: 14px;
                            font-weight: bold;
                            color: #333;
                            margin-bottom: 5px;
                        ">⏰ TIME LEFT</div>
                        <div style="
                            font-size: 24px;
                            font-weight: bold;
                            color: {timer_color};
                            letter-spacing: 2px;
                        ">{hours:02d}:{minutes:02d}:{seconds:02d}</div>
                        <div style="
                            font-size: 12px;
                            color: #666;
                            margin-top: 5px;
                        ">Auto-updating</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Auto-refresh every second for real-time timer updates
                st.markdown(
                    """
                    <script>
                    setTimeout(function() {
                        window.location.reload();
                    }, 1000);
                    </script>
                    """,
                    unsafe_allow_html=True
                )
                
                # Special warning for final minute
                if remaining_time.total_seconds() <= 60:
                    st.warning("⚠️ **Final Minute!** Time is running out!")
                
                # Also add a manual refresh mechanism
                if st.button("🔄 Refresh Timer", key="refresh_timer", help="Click to update timer manually"):
                    st.rerun()
                
                # Add note about timer updates
                st.info("💡 **Timer Note:** Timer updates automatically every second. It also updates when you interact with the test.")
            else:
                # Time's up - auto submit
                st.error("⏰ Time's up! Submitting your test automatically...")
                
                # Get current answers
                questions = test_data['questions']
                student_answers = {}
                
                # Try to get any submitted answers from session state if they exist
                for i in range(len(questions)):
                    question_num = i + 1
                    # Check if answer exists in session state
                    answer_key = f"q_{question_num}"
                    if answer_key in st.session_state:
                        student_answers[answer_key] = st.session_state[answer_key]
                
                # Auto-submit the test
                score_data = calculate_score(questions, student_answers)
                
                # Create result data
                result_data = {
                    "student_name": student_info['name'],
                    "student_email": student_info['email'],
                    "student_id": student_info['student_id'],
                    "test_id": student_info['test_id'],
                    "teacher_name": test_data.get('teacher_name', 'Unknown'),
                    "test_info": {
                        "subject": test_data['subject'],
                        "topics": test_data.get('topics', []),
                        "difficulty": test_data['difficulty'],
                        "created_at": test_data['created_at'],
                        "total_questions": test_data.get('total_questions', len(questions)),
                        "exam_duration_minutes": test_data.get('exam_duration_minutes', 60)
                    },
                    "completed_at": datetime.now().isoformat(),
                    "time_taken_minutes": exam_duration_minutes,
                    "auto_submitted": True,
                    "score": score_data
                }
                
                # Save results to GitHub
                success, message = save_student_result_to_github(
                    result_data, 
                    student_info['name'].replace(' ', '_'), 
                    student_info['test_id'],
                    student_info['student_token']
                )
                
                if success:
                    st.success("✅ Results saved successfully!")
                else:
                    st.warning(f"⚠️ Could not save results: {message}")
                
                # Store results in session state
                st.session_state.test_completed = True
                st.session_state.score_data = score_data
                st.rerun()
            
            st.markdown("---")
            
            # Display questions
            questions = test_data['questions']
            student_answers = {}
            
            for i, question in enumerate(questions):
                question_num = i + 1
                selected_answer = display_question(question, question_num, len(questions))
                if selected_answer:
                    student_answers[f"q_{question_num}"] = selected_answer
                st.markdown("---")
            
            # Finish test button
            if st.button("🏁 Finish Test", type="primary"):
                if len(student_answers) < len(questions):
                    st.warning("⚠️ Please answer all questions before finishing the test.")
                else:
                    # Calculate actual time taken
                    time_taken = datetime.now() - st.session_state.start_time
                    time_taken_minutes = int(time_taken.total_seconds() / 60)
                    
                    # Calculate score
                    score_data = calculate_score(questions, student_answers)
                    
                    # Create result data
                    result_data = {
                        "student_name": student_info['name'],
                        "student_email": student_info['email'],
                        "student_id": student_info['student_id'],
                        "test_id": student_info['test_id'],
                        "teacher_name": test_data.get('teacher_name', 'Unknown'),
                        "test_info": {
                            "subject": test_data['subject'],
                            "topics": test_data.get('topics', []),
                            "difficulty": test_data['difficulty'],
                            "created_at": test_data['created_at'],
                            "total_questions": test_data.get('total_questions', len(questions)),
                            "exam_duration_minutes": test_data.get('exam_duration_minutes', 60)
                        },
                        "completed_at": datetime.now().isoformat(),
                        "time_taken_minutes": time_taken_minutes,
                        "auto_submitted": False,
                        "score": score_data
                    }
                    
                    # Save results to GitHub
                    success, message = save_student_result_to_github(
                        result_data, 
                        student_info['name'].replace(' ', '_'), 
                        student_info['test_id'],
                        student_info['student_token']
                    )
                    
                    if success:
                        st.success("✅ Results saved successfully!")
                    else:
                        st.warning(f"⚠️ Could not save results: {message}")
                    
                    # Store results in session state
                    st.session_state.test_completed = True
                    st.session_state.score_data = score_data
                    st.rerun()
    
    # Display results
    elif st.session_state.test_completed:
        display_results(st.session_state.score_data)
        
        # Reset test
        if st.button("🔄 Take Another Test"):
            st.session_state.test_loaded = False
            st.session_state.test_data = None
            st.session_state.student_info = None
            st.session_state.test_completed = False
            st.session_state.test_started = False
            st.session_state.start_time = None
            st.rerun()
    
    # Information section
    with st.expander("ℹ️ How to take the test"):
        st.markdown("""
        ### Steps to take the test:
        1. **Enter Information**: Fill in your name and Test ID (email and student ID are optional)
        2. **Student Token**: Enter your GitHub Personal Access Token
        3. **Load Test**: Click "Load Test" to fetch the test questions
        4. **Start Test**: Click "Start Test" to begin the timed exam
        5. **Answer Questions**: Read each question carefully and select your answer
        6. **Monitor Time**: Keep an eye on the countdown timer at the top
        7. **Complete Test**: Click "Finish Test" when done or time will auto-submit
        8. **View Results**: Get your score and detailed explanations
        
        ### Timer Features:
        - ⏰ **Countdown Timer**: Shows exact time remaining in HH:MM:SS format
        - 📍 **Sticky Timer**: Fixed timer on right side that stays visible while scrolling
        - 🟢 **Green Timer**: More than 10 minutes remaining
        - 🟡 **Orange Timer**: 5-10 minutes remaining  
        - 🔴 **Red Timer**: Less than 5 minutes remaining
        - 🔄 **Real-time Updates**: Timer updates every second automatically
        - ⚡ **Auto-Submit**: Test submits automatically when time expires
        
        ### Test ID Format:
        - Test IDs follow the format: `TEACHERNAME_YYYYMMDD_XX`
        - Example: `AMIT_20250105_33`
        - Get this from your teacher
        
        ### Important Notes:
        - ⚠️ **Timer cannot be paused** once you start the test
        - Make sure you have a stable internet connection
        - Answer all questions before time runs out
        - Your progress is automatically saved
        - Results are automatically saved to GitHub
        - The test shows teacher name, duration, and creation date
        
        ### Features:
        - ✅ Interactive test interface with timer
        - ✅ Teacher and test information display
        - ✅ Real-time countdown timer with color coding
        - ✅ Automatic submission when time expires
        - ✅ Instant scoring and feedback
        - ✅ Detailed explanations for each answer
        - ✅ Results saved to GitHub with time tracking
        """)

if __name__ == "__main__":
    main() 
