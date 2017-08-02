from lib.config import *
from flask import Flask, render_template, request, url_for, redirect, session, flash
from functools import wraps
from lib import functions as fcn

app = Flask(__name__)
app.secret_key = SECRET_KEY

def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('you need to login first.')
            return redirect(url_for('login'))
    return wrap


''' Home '''

@app.route('/')
def index():
    return render_template('index.html')

''' Login page '''

@app.route("/login", methods=['GET','POST'])
def login():
    error = None
    session.pop('logged_in',None)
    session.pop('user', None)
    session.pop('role',None)
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        result = fcn.fetch_username_and_password(username,password) 
        if result[0] !=True:                                    #if the credentials are invalid
            error = "incorrect credentials"
        else:
            if result[1] == True:                               #if the user is admininstrator
                session['logged_in'] = True
                session['user'] = username
                session['role'] = 'admin'
                return redirect(url_for('admin'))
            else:                                               #if the user is a regular user 
                session['logged_in'] = True           
                session['user'] = username
                session['role'] = 'user'
                return redirect(url_for('answers'))
    return render_template('login.html', error = error)

''' the administrator's page '''

@app.route('/admin')
@login_required
def admin():
    role = session['role']
    if role !="admin":
        return redirect(url_for('permission_error'))
    else:
        return render_template('admin.html')

'''logout route '''

@app.route("/logout")
def logout():
    session.pop("logged_in",None)
    flash('you are logged out successfully!')
    return redirect(url_for('login'))

'''page of question lists for the users '''

@app.route("/answers", methods=['GET'])
@login_required
def answers():
    questionID = fcn.fetch_questions_db()[0]
    questionText = fcn.fetch_questions_db()[1]
    return render_template("answers.html", 
        numberOfQuestions = len(questionID),
        id = questionID,
        text = questionText)

''' save answers in database page '''

@app.route("/success", methods=['POST'])
@login_required
def success():
    sessionKey = session ['user']
    answers = sorted(list(request.form.items()))
    fcn.split_and_save(sessionKey,answers)
    return render_template("success.html")

'''create a user in system page '''

@app.route('/adduser', methods = ['GET','POST'])
@login_required
def define_user():
    role = session['role']
    if request.method =='GET':
        return render_template('add_user.html')
    else:
        fcn.hashing_and_save(request.form.items())
        flash('User added successfuly!')
        return render_template('add_user.html')

''' access denied page '''

@app.route('/permissionError')
def permission_error():
    return render_template("permission_error.html")

''' add question page '''

@app.route("/addDataAdmin", methods=['POST','GET'])
@login_required
def add_question():
        questionList = fcn.questions_statistics()
        if request.method == 'GET':
            return render_template('add_data_admin.html',data = questionList, length = len(questionList))
        else:
            fcn.save_questions_to_DB(request.form.items()[0][1])
            #return render_template('add_data_admin.html',data = questionList, length = len(questionList))
            return redirect(url_for('add_question'))
'''Visualizing the data '''

@app.route('/visualization', methods=['GET'])
@login_required 
def visualization():
    results = fcn.questions_statistics()
    noUsersAnswered = len(fcn.users_answered())
    lengthOfResults = len(results)
    return render_template('statistics.html',results=results,users = noUsersAnswered, length = lengthOfResults)


@app.route('/viewQuestions')
@login_required
def view_questions():
    results = fcn.questions_statistics()
    lengthOfResults = len(results)
    return render_template('list_of_questions.html',data = results, length = lengthOfResults)

''' running the app '''

if __name__ == '__main__':
    app.debug = True
    app.run()