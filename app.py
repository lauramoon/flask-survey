from flask import Flask, request, render_template, redirect, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask import flash, session
from surveys import surveys

app = Flask(__name__)

app.config['SECRET_KEY'] = "ilovecats"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

response = []
counter = {0: 0}

@app.route('/')
def survey_start():
    """show survey selection form"""
    return render_template("index.html", surveys=surveys)

@app.route('/survey_info', methods=['POST'])
def survey_info():
    """get selected survey and store in flask session"""
    session['survey_key'] = request.form["survey"]
    return redirect('/start')

@app.route('/start')
def show_start():
    """ show starting info for selected survey"""
    survey_key = session.get('survey_key', 'none')
    if survey_key != 'none':
        title = surveys[survey_key].title
        instructions = surveys[survey_key].instructions
        return render_template("start.html", title=title, instructions=instructions)
    else:
        return render_template('index.html')

@app.route('/start_survey', methods=['POST'])
def track_survey():
    """reset response list, redirect to first question"""
    session['response'] = []
    return redirect('questions/0')

@app.route('/questions/<int:num>')
def serve_question(num):
    """serve the next question in the survey"""
    resp_count = len(session['response'])
    survey = surveys[session['survey_key']]

    # make sure that the question requested matches the one expected
    if num == resp_count:
        question_class = survey.questions[num]
        return render_template("question.html", question=question_class, num=num)
    else:
        if resp_count >= len(survey.questions):
            flash('You have completed the survey. There are no more questions to answer')
            return redirect('/thankyou')
        else:
            flash('You are attempting at access an inaccessible question. Please answer the quesiton below.')
            return redirect(f'/questions/{resp_count}')

@app.route('/answer', methods=["POST"])
def save_answer():
    """store the selected answer in the correct place in the the response list,
    direct to next question or thank you page if complete"""
    res = session['response']
    survey = surveys[session['survey_key']]
    num = int(request.form['num'])
    ans = {'choice': request.form['choice']}
    if 'text' in request.form:
        ans['text'] = request.form['text']

    # if the 'back' button is used, previous question can be accessed
    if len(res) == num:
        res.append(ans)
    else: 
        res[num] = ans
    session['response'] = res

    if len(res) >= len(survey.questions):
        return redirect('/thankyou')
    else:
        return redirect(f'/questions/{len(res)}')

@app.route('/thankyou')
def thank_you_page():
    """show thank you page"""

    return render_template('thankyou.html', questions=surveys[session['survey_key']].questions)
