from flask import Flask, render_template, request, redirect, url_for, flash
from correspondentai import CorrespondentAI
from user import User
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # for flash messages

# Initialize CorrespondentAI with your LLM API key
ai = CorrespondentAI(llm_api_key='your_api_key_here')

@app.route('/')
def index():
    return render_template('index.html', users=ai.users)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        interests = request.form['interests'].split(',')
        sites = request.form['sites'].split(',')
        new_user = User(name, email, interests, sites)
        ai.add_user(new_user)
        flash('User added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_user.html')

@app.route('/run_report')
def run_report():
    ai.run_weekly_report()
    flash('Weekly report generated and sent to all users!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)