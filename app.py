from flask import Flask, render_template, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] ='verysecret'
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)  
app.app_context().push()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Employee).get(int(user_id))

class Employee(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    streak = db.Column(db.Integer, default=0) 
    menus = db.relationship('Menu', backref='restaurant', lazy=True)


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.now().date())
    name = db.Column(db.String(50), unique=True, nullable=False)
    vote = db.Column(db.Integer, default=0)
    description = db.Column(db.String(255), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=6, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = Employee.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            flash('That username already exists. Please choose a different one.')
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=6, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Employee.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('vote'))
    return render_template('login.html', form=form)


@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    restaurants,all_menus,highest_voted_menu = get_restaurant_and_menus()
    return render_template('vote.html', user=current_user.username, restaurants=restaurants, all_menus=all_menus, selected_menu = highest_voted_menu)


@app.route('/submit-vote', methods=['POST'])
def submit_vote():
    restaurants,all_menus,_ = get_restaurant_and_menus()
    menu_id = request.form.get('selectedMenuId')
    selected_menu = Menu.query.get(menu_id)
    print('voteee   ',selected_menu.name, selected_menu.vote)
    if selected_menu:
        # Increment the vote count
        print('voteee   ',selected_menu.vote)
        selected_menu.vote = selected_menu.vote + 1
        db.session.commit()
        highest_voted_menu = Menu.query.order_by(Menu.vote.desc()).first().name
        return render_template('vote.html', user=current_user.username, restaurants=restaurants, all_menus=all_menus, selected_menu = highest_voted_menu)
    print('voteee   ',selected_menu.name, selected_menu.vote)
    return redirect(url_for('vote'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = Employee(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    return render_template('admin.html')

@app.route('/addRestaurant', methods=['GET', 'POST'])
@login_required
def addRestaurant():
    return render_template('admin.html')

@app.route('/addMenu', methods=['GET', 'POST'])
@login_required
def addMenu():
    return render_template('admin.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



def get_restaurant_and_menus():
    restaurants = Restaurant.query.all()
    highest_voted_menu = Menu.query.order_by(Menu.vote.desc()).first().name
    all_menus = {}

    for restaurant in restaurants:
        menus = Menu.query.filter_by(restaurant_id=restaurant.id).all()
        all_menus[restaurant.id] = menus
    return restaurants,all_menus,highest_voted_menu

if __name__ =='__main__':
    app.run(debug=True)