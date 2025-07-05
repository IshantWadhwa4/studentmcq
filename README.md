# Teacher-Student MCQ Test System

A comprehensive Streamlit-based system for teachers to create AI-powered MCQ tests and for students to take them with instant feedback.

## Features

### Teacher Application (`teacher_app.py`)
- 📚 **Subject-based Question Generation**: Support for Mathematics, Physics, Chemistry, and Biology
- 🎯 **Topic Selection**: Choose from curriculum-based topics defined in `syllabus.py`
- 🤖 **AI-Powered**: Uses OpenAI GPT-4 to generate high-quality questions
- 📊 **Difficulty Levels**: Easy, Medium, Hard, or Mix
- 💾 **GitHub Integration**: Automatically saves tests to GitHub repository
- 🔗 **Shareable Tests**: Generate unique exam tokens for students
- 📋 **Test Preview**: Review questions before sharing

### Student Application (`student_app.py`)
- 👨‍🎓 **Student-Friendly Interface**: Clean, interactive test-taking experience
- 📖 **Dynamic Test Loading**: Load tests using exam tokens from GitHub
- ⏱️ **Real-time Progress**: Track progress through questions
- 📊 **Instant Results**: Get immediate score and detailed explanations
- 💾 **Result Storage**: Automatically save results to GitHub
- 📥 **Downloadable Results**: Export results as JSON files

## Setup Instructions

### 1. Prerequisites
- Python 3.7+
- OpenAI API key
- GitHub account with personal access token

### 2. Installation
```bash
# Clone or download the project
cd teacher_student_MCQ

# Install dependencies
pip install -r requirements.txt
```

### 3. GitHub Configuration
The GitHub repository and access token are pre-configured in the applications:
- Repository: `IshantWadhwa4/data_tsmcq`
- Test files path: `questions`
- Student results path: `students_solution`

### 4. OpenAI API Setup
1. Create an OpenAI account at https://platform.openai.com/
2. Generate an API key
3. Ensure you have sufficient credits for question generation

## Usage

### For Teachers

1. **Run the Teacher Application**
   ```bash
   streamlit run teacher_app.py
   ```

2. **Configure Your Test**
   - Select subject (Mathematics, Physics, Chemistry, Biology)
   - Choose topics from the syllabus
   - Add additional information (optional)
   - Set number of questions (5-50)
   - Choose difficulty level

3. **API Configuration**
   - Enter your OpenAI API key
   - GitHub configuration is pre-set and displayed

4. **Generate and Share**
   - Click "Generate Test"
   - Copy the exam token
   - Share the exam token with students

### For Students

1. **Run the Student Application**
   ```bash
   streamlit run student_app.py
   ```

2. **Enter Information**
   - Student name (required)
   - Email address (optional)
   - Student ID (optional)
   - Exam token from teacher (required)

3. **Take the Test**
   - Load the test using the exam token
   - Answer all questions
   - Click "Finish Test" to get results

## File Structure

```
teacher_student_MCQ/
├── teacher_app.py          # Teacher application
├── student_app.py          # Student application
├── syllabus.py            # Subject syllabus data
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## GitHub Repository Structure

The GitHub repository will have the following structure:
```
IshantWadhwa4/data_tsmcq/
├── questions/             # Generated test files
│   ├── test_1234567890.json
│   └── test_1234567891.json
└── students_solution/     # Student test results
    ├── John_Doe_test_1234567890_1234567892.json
    └── Jane_Smith_test_1234567890_1234567893.json
```

## Sample Test Data Structure

### Test File Format
```json
{
  "exam_token": "test_1234567890",
  "created_at": "2024-01-15T10:30:00",
  "subject": "Mathematics",
  "topics": ["Integral Calculus", "Matrices and Determinants"],
  "difficulty": "Medium",
  "num_questions": 10,
  "questions": [
    {
      "question_number": 1,
      "question_text": "What is the integral of x²?",
      "options": {
        "A": "x³/3 + C",
        "B": "2x + C",
        "C": "x³ + C",
        "D": "3x² + C"
      },
      "correct_answer": "A",
      "explanation": "The integral of x² is x³/3 + C using the power rule",
      "topic": "Integral Calculus",
      "subtopic": "Basic Integration",
      "difficulty": "Easy"
    }
  ]
}
```

### Student Result Format
```json
{
  "student_name": "John Doe",
  "student_email": "john@example.com",
  "exam_token": "test_1234567890",
  "completed_at": "2024-01-15T11:00:00",
  "score": {
    "total_questions": 10,
    "correct_answers": 8,
    "score_percentage": 80.0,
    "results": [...]
  }
}
```

## Customization

### Adding New Subjects
1. Edit `syllabus.py` to add new subjects and topics
2. Update the subjects list in both applications

### Modifying Question Generation
1. Edit the `create_openai_prompt()` function in `teacher_app.py`
2. Adjust the prompt template for different question styles

### Changing GitHub Structure
1. Modify `GITHUB_PATH` and `RESULTS_PATH` constants
2. Update the file naming conventions

## Security Notes

- **API Keys**: Never commit API keys to version control
- **GitHub Tokens**: Use tokens with minimal required permissions
- **Repository**: Consider using private repositories for sensitive data
- **Student Access**: Students only need read access to test files

## Troubleshooting

### Common Issues

1. **"Test not found" Error**
   - Verify the exam token is correct
   - Check GitHub repository name and permissions
   - Ensure the test file was created successfully

2. **OpenAI API Errors**
   - Check your API key is valid
   - Verify sufficient credits in your OpenAI account
   - Ensure you have access to GPT-4 model

3. **GitHub API Errors**
   - The GitHub integration is pre-configured
   - Contact the administrator if you encounter repository access issues

### Debug Mode

To enable debug logging, add this to the beginning of your Python files:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Support

For issues and questions:
1. Check the troubleshooting section
2. Verify your API keys and permissions
3. Review the GitHub repository structure
4. Check Streamlit logs for detailed error messages

## License

This project is open source and available under the MIT License. 