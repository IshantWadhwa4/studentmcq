import streamlit as st
import json
import requests
import base64
import time
from datetime import datetime

# GitHub configuration
GITHUB_TOKEN = "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"  # Replace with your new token
GITHUB_REPO = "IshantWadhwa4/data_tsmcq"
GITHUB_PATH = "questions"  # Path where test files are stored
RESULTS_PATH = "students_solution"  # Path where student results will be stored

def load_test_from_github(exam_token):
    """Load test data from GitHub repository"""
    try:
        # GitHub API endpoint
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{exam_token}.json"
        
        # Headers
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
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

def save_student_result_to_github(result_data, student_name, exam_token):
    """Save student result to GitHub repository"""
    try:
        # Create filename with timestamp
        timestamp = int(time.time())
        filename = f"{student_name}_{exam_token}_{timestamp}.json"
        
        # GitHub API endpoint
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{RESULTS_PATH}/{filename}"
        
        # Prepare the content
        content = json.dumps(result_data, indent=2)
        encoded_content = base64.b64encode(content.encode()).decode()
        
        # API request data
        data = {
            "message": f"Add student result: {student_name} - {exam_token}",
            "content": encoded_content,
            "branch": "main"  # or your default branch
        }
        
        # Headers
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
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
                exam_token = st.text_input("Exam Token*", help="Enter the exam token provided by your teacher")
            
            # GitHub configuration (Display only)
            st.markdown("### 📂 GitHub Configuration")
            col3, col4 = st.columns(2)
            with col3:
                st.info(f"Repository: {GITHUB_REPO}")
            with col4:
                st.info(f"Test Path: {GITHUB_PATH}")
            
            submit_button = st.form_submit_button("📖 Load Test", type="primary")
            
            if submit_button:
                if not student_name or not exam_token:
                    st.error("Please fill in all required fields (marked with *)")
                else:
                    # Load test
                    with st.spinner("Loading test..."):
                        success, test_data = load_test_from_github(exam_token)
                        
                        if success:
                            st.session_state.test_loaded = True
                            st.session_state.test_data = test_data
                            st.session_state.student_info = {
                                "name": student_name,
                                "email": email,
                                "student_id": student_id,
                                "exam_token": exam_token
                            }
                            st.success("✅ Test loaded successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to load test: {test_data}")
    
    # Display test
    elif st.session_state.test_loaded and not st.session_state.test_completed:
        test_data = st.session_state.test_data
        student_info = st.session_state.student_info
        
        # Test header
        st.header(f"📖 {test_data['subject']} Test")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Subject:** {test_data['subject']}")
        with col2:
            st.info(f"**Questions:** {len(test_data['questions'])}")
        with col3:
            st.info(f"**Difficulty:** {test_data['difficulty']}")
        
        if test_data.get('topics'):
            st.info(f"**Topics:** {', '.join(test_data['topics'])}")
        
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
                # Calculate score
                score_data = calculate_score(questions, student_answers)
                
                # Create result data
                result_data = {
                    "student_name": student_info['name'],
                    "student_email": student_info['email'],
                    "student_id": student_info['student_id'],
                    "exam_token": student_info['exam_token'],
                    "test_info": {
                        "subject": test_data['subject'],
                        "topics": test_data.get('topics', []),
                        "difficulty": test_data['difficulty'],
                        "created_at": test_data['created_at']
                    },
                    "completed_at": datetime.now().isoformat(),
                    "score": score_data
                }
                
                # Save results to GitHub
                success, message = save_student_result_to_github(
                    result_data, 
                    student_info['name'].replace(' ', '_'), 
                    student_info['exam_token']
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
        
        # Download results
        if st.button("📥 Download Results"):
            result_json = json.dumps(st.session_state.score_data, indent=2)
            st.download_button(
                label="Download Results (JSON)",
                data=result_json,
                file_name=f"test_results_{int(time.time())}.json",
                mime="application/json"
            )
        
        # Reset test
        if st.button("🔄 Take Another Test"):
            st.session_state.test_loaded = False
            st.session_state.test_data = None
            st.session_state.student_info = None
            st.session_state.test_completed = False
            st.rerun()
    
    # Information section
    with st.expander("ℹ️ How to take the test"):
        st.markdown("""
        ### Steps to take the test:
        1. **Enter Information**: Fill in your name and exam token (email and student ID are optional)
        2. **Load Test**: Click "Load Test" to fetch the test questions
        3. **Answer Questions**: Read each question carefully and select your answer
        4. **Complete Test**: Click "Finish Test" when you've answered all questions
        5. **View Results**: Get your score and detailed explanations
        
        ### Important Notes:
        - Make sure to answer all questions before finishing
        - You can review your answers before submitting
        - Results are automatically saved to GitHub
        - Explanations are provided for each question
        
        ### Features:
        - ✅ Interactive test interface
        - ✅ Instant scoring and feedback
        - ✅ Detailed explanations for each answer
        - ✅ Results saved to GitHub
        - ✅ Downloadable results
        """)

if __name__ == "__main__":
    main() 
