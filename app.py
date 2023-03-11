from flask import Flask, redirect, render_template, request, url_for, flash, session
from flask_login import current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '392b6ac18ee75ca52d1d420a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///.//test.db'
db = SQLAlchemy(app)
ticket = 0


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.name


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.name


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ticket_no = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.name

@app.route('/logout')
def logout():
    return redirect("/")

@app.route("/", methods=['POST','GET'])
def home():
    global user_type
    if request.method == 'POST':
        user_type = request.form.get('usertype')
        return redirect('/login')
    return render_template('index.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if user in session:
        return redirect('/useroradmin')
    return render_template('login.html')


@app.route("/useroradmin", methods=['POST','GET'])
def useroradmin():
    if request.method == 'POST':
        email = request.form.get('email')    
        password = request.form.get('password')
        if user_type == 'admin':
            admin = Admin.query.filter_by(email=email, password=password).first()
            print(admin)
            if admin:
                return redirect('/admin')
        elif user_type == 'user':
            user = User.query.filter_by(email=email, password=password).first()
            if user:            
                return redirect('/user')
            
    
    flash("Invalid Username or Password")

    return render_template('login.html')
    

@app.route("/user", methods=['GET','POST'])
def user():
    global ticket
    if request.method == 'POST':
        ticket += 1
        title = request.form.get('Complaints')
        dept_name = request.form.get('Department Name')
        print(request.form,title, dept_name)
        if title and dept_name:
            message1 = Message(id=ticket,content=title,ticket_no=ticket, title=dept_name)
            db.session.add(message1)
            db.session.commit()
            flash("Your complaint has been raised successfully")
        else:
            flash("Your complaint was not successful. Please fill in all the options and try again.")
            return redirect('/new_issue')
    return render_template('user.html')

@app.route("/admin_response", methods=['POST'])
def admin_response():
    title = request.form.get('id')
    print(request.form)
    previous_issues = Message.query.filter_by(ticket_no = title)    
    return render_template('admin_response.html', previous_issues=previous_issues)

@app.route("/admin", methods=['GET'])
def admin():
    global user_type
    boolean = False
    if user_type == 'admin':
        boolean = True
    previous_issues = Message.query.limit(10).all()
    return render_template('previous.html',previous_issues=previous_issues, boolean=boolean)

# @logout_user
# @app.route("logout", methods=['GET'])
# def logout():
#     session.pop('user')
#     return redirect('/home')

@app.route("/previous_issue", methods=['POST', 'GET'])
def previous_issue():
    global user_type
    boolean = False
    if user_type == 'admin':
        boolean = True
    previous_issues = Message.query.limit(5).all()
    return render_template('previous.html', previous_issues=previous_issues, boolean=boolean)

@app.route("/new_issue")
def new_issue():
    return render_template('user_complaint.html')

@app.route("/issue", methods=['POST', 'GET'])
def issue():
    if request.form.get('new_issue'):
        return redirect("/new_issue")
    else:
        return redirect("/previous_issue")
    
@app.errorhandler(404)
def page_not_found(error):
    flash("This Page does not exist")
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_server(error):
    flash("Internal Server Error")
    return render_template('index.html'), 500


if __name__ == '__main__':
    app.run(debug=True)