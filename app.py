from flask import Flask, request, render_template, redirect, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask import flash
from surveys import satisfaction_survey

app = Flask(__name__)

app.config['SECRET_KEY'] = "ilovecats"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

response = []
counter = {0: 0}

@app.route('/')
def survey_start():
    counter[0] = 0
    del response[:]
    title = satisfaction_survey.title
    instructions = satisfaction_survey.instructions
    return render_template("index.html", title=title, instructions=instructions)

@app.route('/questions/<int:num>')
def serve_question(num):
    if num == counter[0]:
        question_class = satisfaction_survey.questions[num]
        question = question_class.question
        choices = question_class.choices
        return render_template("question.html", question=question, choices=choices)
    else:
        if counter[0] >= len(satisfaction_survey.questions):
            flash('You have completed the survey. There are no more questions to answer')
            return redirect('/thankyou')
        else:
            flash('You are attempting at access an inaccessible question. Please answer the quesiton below.')
            return redirect(f'/questions/{counter[0]}')

@app.route('/answer', methods=["POST"])
def save_answer():
    choice = request.form["choice"]
    response.append(choice)
    counter[0] += 1

    if counter[0] >= len(satisfaction_survey.questions):
        return redirect('/thankyou')
    else:
        return redirect(f'/questions/{counter[0]}')

@app.route('/thankyou')
def thank_you_page():
    return render_template('thankyou.html', response=response)
