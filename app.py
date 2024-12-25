from flask import Flask, render_template, request, session, jsonify, send_file, redirect, url_for
from flask_cors import CORS
from flask_restful import Api, Resource, marshal_with, fields
from config import DevConfig,BASE_DIR
from database import db
from fpdf import FPDF
import pandas as pd
import os


# File paths
ceo_file = os.path.join(BASE_DIR, "data/CEO sheet.xlsx")
technical_file = os.path.join(BASE_DIR, "data/technical sheet.xlsx")
pdf_path = os.path.join(BASE_DIR, "data/improvement_suggestions.pdf")

# Load Excel Data
ceo_data = pd.read_excel(ceo_file, sheet_name=0)
technical_data = pd.read_excel(technical_file, sheet_name=0)

# Extract questions and topics
def get_questions(data):
    questions = []
    for _, row in data.iterrows():
        topic = row.iloc[0]
        possible_answer = row.iloc[1] if len(row) > 1 else None
        if pd.isna(possible_answer):  # Treat as a topic if Column B is blank
            questions.append((topic, None))
        else:  # Treat as a question if Column B has a value
            questions.append((topic, "Yes/No"))
    return questions

ceo_questions = get_questions(ceo_data)
technical_questions = get_questions(technical_data)


# import models class to create the tables below
# from models import User

# Initialize the flask app
app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')

# Load environments
app.secret_key = DevConfig.FLASK_SECRET_KEY
app.config.from_object(DevConfig)

# Initialize database
db.init_app(app)

# Enable Cors
CORS(app)

# Initialize Api
api = Api(app)


# This one will create the tables in the databaes but first you must import the models class
# to this files in order for sqlalchemy to know about theme
with app.app_context():
    db.create_all()

# Class That represent our CRUD
class BaseAPI(Resource):
    def get(self):
        return {'message': "Tikatar base api"}

# Example of User endpoint with simple get request it will create a user in databse with the name User
# class UserEndpoint(Resource):
#     #the marshal_with lets us return an instance with the fields that we want to return without serializing  
#     @marshal_with({"id": fields.Integer, "username": fields.String})
#     def get(self):
#         user = User()
#         user.set_username("User")
#         db.session.add(user)
#         db.session.commit()
#         return user
        
# Endpoints
# api.add_resource(BaseAPI, '/')
# api.add_resource(UserEndpoint, '/users')



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mode', methods=['GET', 'POST'])
def mode():
    if request.method == 'POST':
        mode_choice = request.form.get('mode')
        if mode_choice == 'manual':
            return render_template('manual.html')
        elif mode_choice == 'upload':
            return render_template('upload.html')
    return render_template('mode.html')

@app.route('/manual', methods=['POST'])
def manual():
    role = request.form.get('role')
    session['role'] = role
    if role == 'ceo':
        questions = ceo_questions
    else:
        questions = technical_questions

    session['questions'] = questions
    session['current_index'] = 0
    session['answers'] = {}

    if not questions:
        return "<h2>No questions available. Please check the data source.</h2>"

    return redirect(url_for('question'))

@app.route('/question', methods=['GET', 'POST'])
def question():
    questions = session.get('questions', [])
    current_index = session.get('current_index', 0)

    if not questions:
        return "<h2>No questions found. Please start again.</h2>"

    if request.method == 'POST':
        answer = request.form.get('answer')
        if current_index < len(questions):
            current_question = questions[current_index]
            if current_question[1] is not None:  # Save answer if it's a question
                session['answers'][current_question[0]] = answer

        session['current_index'] += 1
        current_index = session['current_index']

    if current_index >= len(questions):
        return redirect(url_for('submit'))

    current_question = questions[current_index]
    return render_template(
        'question.html',
        question=current_question[0],
        is_question=current_question[1] is not None  # True if it's a question
    )

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    answers = session.get('answers', {})
    yes_count = sum(1 for answer in answers.values() if answer.lower() == 'yes')

    if len(answers) == 0:
        grade = 0
    else:
        grade = (yes_count / len(answers)) * 100

    # Generate improvement PDF for "No" answers
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Improvement Suggestions", ln=True, align='C')

    for question, answer in answers.items():
        if answer.lower() == 'no':
            pdf.cell(200, 10, txt=f"Improve on: {question}".encode('latin-1', 'replace').decode('latin-1'), ln=True)

    pdf.output(pdf_path)

    return render_template('submit.html', grade=grade)

@app.route('/download')
def download():
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    return "<h2>The file does not exist. Complete the questionnaire first!</h2>"

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_input = request.json.get('message', '').lower()

        # Step 1: Role Selection
        if 'role' not in session:
            if user_input in ['ceo', 'technical']:
                session['role'] = user_input
                session['questions'] = ceo_questions if user_input == 'ceo' else technical_questions
                session['current_index'] = 0
                session['answers'] = {}
                return _ask_next_question()
            return jsonify({
                'response': "Are you a CEO or a Technical Person?",
                'buttons': [
                    {'text': 'CEO', 'value': 'ceo'},
                    {'text': 'Technical', 'value': 'technical'}
                ]
            })

        # Step 2: Handle questions and answers
        if 'questions' in session and 'current_index' in session:
            if user_input in ['yes', 'no', 'proceed']:
                current_index = session['current_index']
                questions = session['questions']
                if user_input != 'proceed':  # Skip saving for topics
                    session['answers'][questions[current_index][0]] = user_input
                session['current_index'] += 1
                return _ask_next_question()

        return jsonify({'response': "Something went wrong. Please restart the chatbot."})

    return render_template('chatbot.html')

def _ask_next_question():
    questions = session.get('questions', [])
    current_index = session.get('current_index', 0)

    if current_index >= len(questions):  # Completed
        return _complete_questionnaire()

    current_question = questions[current_index]
    if current_question[1] is None:  # Topic
        return jsonify({
            'response': f"Topic: {current_question[0]}",
            'buttons': [
                {'text': 'Proceed', 'value': 'proceed'}
            ]
        })

    return jsonify({
        'response': f"Question: {current_question[0]}",
        'buttons': [
            {'text': 'Yes', 'value': 'yes'},
            {'text': 'No', 'value': 'no'}
        ]
    })

def _complete_questionnaire():
    answers = session.get('answers', {})
    yes_count = sum(1 for answer in answers.values() if answer.lower() == 'yes')
    grade = (yes_count / len(answers)) * 100 if answers else 0

    # Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Improvement Suggestions", ln=True, align='C')

    for question, answer in answers.items():
        if answer.lower() == 'no':
            pdf.cell(200, 10, txt=f"Improve on: {question}".encode('latin-1', 'replace').decode('latin-1'), ln=True)

    pdf.output(pdf_path)

    return jsonify({
        'response': f"You have completed the questionnaire! Your grade: {grade:.2f}%.",
        'buttons': [
            {'text': 'Download PDF', 'value': 'download'},
            {'text': 'Restart', 'value': 'reset'}
        ]
    })


# Running our flask server
if __name__ == '__main__':
    app.run(debug=True)