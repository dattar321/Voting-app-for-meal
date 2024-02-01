from flask import Flask, render_template, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, validators
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta, date
from apscheduler.schedulers.background import BackgroundScheduler

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

#database classes
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
    name = db.Column(db.String(80), unique=True, nullable=False)
    vote = db.Column(db.Integer, default=0)
    description = db.Column(db.String(255), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

class MenuHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, default=datetime.now)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship('Employee', backref='votes')
    menu = db.relationship('Menu', backref='votes')

#Forms 
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=6, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = Employee.query.filter_by(username=username.data).first()
        if existing_user_username:
            flash('That username already exists. Please choose a different one.')
            raise ValidationError('That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=6, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

class AddRestaurantForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(min=10, max=30)], render_kw={"placeholder": "Enter Restaurant Name"})
    submit = SubmitField('Add Restaurant')

class AddMenuForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(min=6, max=30)], render_kw={"placeholder": "Enter Restaurant Name"})
    description = StringField(validators=[InputRequired(), Length(min=10, max=80)], render_kw={"placeholder": "Enter Description"})
    submit = SubmitField('Add Menu')

class choicesForm(FlaskForm):
    restaurants = Restaurant.query.all()
    choices = []
    for i in restaurants:
        choices.append((i.id,i.name))
    dropdown = SelectField('Choose an option', choices=choices, validators=[validators.InputRequired()])

#routes
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
    btn = 1
    user_id = current_user.id
    last_vote = Vote.query.filter_by(user_id=user_id).order_by(Vote.timestamp.desc()).first()
    if last_vote:
        if last_vote or (datetime.utcnow() - last_vote.timestamp).total_seconds() < 86400:
            btn = 0
    restaurants,all_menus,highest_voted_menu = get_restaurant_and_menus()
    return render_template('vote.html', user=current_user.username, restaurants=restaurants, all_menus=all_menus, selected_menu = highest_voted_menu,btn=btn)


@app.route('/submit-vote', methods=['POST'])
def submit_vote():
    restaurants,all_menus,_ = get_restaurant_and_menus()
    user_id = current_user.id
    menu_id = request.form.get('selectedMenuId')
    last_vote = Vote.query.filter_by(user_id=user_id).order_by(Vote.timestamp.desc()).first()
    if not last_vote or (datetime.utcnow() - last_vote.timestamp).total_seconds() > 86400:
        selected_menu = Menu.query.get(menu_id)
        if selected_menu:
            selected_menu.vote = selected_menu.vote + 1
            new_vote = Vote(user_id=user_id, menu_id=menu_id)
            db.session.add(new_vote)
            db.session.commit()
    highest_voted_menu = highest_voted_menu = current_menu()
    return render_template('vote.html', user=current_user.username, restaurants=restaurants, all_menus=all_menus, selected_menu = highest_voted_menu,btn=0)
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
    form = AddRestaurantForm()
    if form.name.data:
        existing_restaurant = Restaurant.query.filter_by(name=form.name.data).first()
        if not existing_restaurant:
            new_restaurant = Restaurant(name=form.name.data)
            db.session.add(new_restaurant)
            db.session.commit()
            return redirect(url_for('admin'))
    return render_template('addRestaurant.html', form=form)

@app.route('/addMenu', methods=['GET', 'POST'])
@login_required
def addMenu():    
    form = AddMenuForm()
    choices = choicesForm()
    if choices.dropdown.data and form.name.data:
        existing_menu = Menu.query.filter_by(name=form.name.data).first()
        if not existing_menu:
            new_menu = Menu(date = datetime.now().date(),name = form.name.data,restaurant_id = choices.dropdown.data, description=form.description.data,)
            db.session.add(new_menu)
            db.session.commit()
            return redirect(url_for('admin'))
    return render_template('addMenu.html',form=form, choices=choices)

@app.route('/mealConfirm', methods=['GET', 'POST'])
@login_required
def mealConfirm():
    highest_voted_menu = Menu.query.order_by(Menu.vote.desc()).first()
    today_date = date.today()
    today_in_menu_history = MenuHistory.query.filter(MenuHistory.datetime >= today_date, MenuHistory.datetime < today_date + timedelta(days=1)).first()
    if not today_in_menu_history:
        first = MenuHistory.query.order_by(MenuHistory.datetime.desc()).first().restaurant_id
        second = MenuHistory.query.order_by(MenuHistory.datetime.desc()).offset(1).first().restaurant_id
        if first and second and first == second and first == highest_voted_menu.restaurant_id:
            k=1
            while k<3 and first == highest_voted_menu.restaurant_id:
                highest_voted_menu = Menu.query.order_by(Menu.vote.desc()).offset(k).first()
                k = k+1
        new_menu_history = MenuHistory(datetime=today_date, menu_id=highest_voted_menu.id, restaurant_id=highest_voted_menu.restaurant_id)
        db.session.add(new_menu_history)
        db.session.commit()
    else:
        highest_voted_menu_id = MenuHistory.query.order_by(MenuHistory.id.desc()).first().menu_id
        highest_voted_menu = Menu.query.filter_by(id=highest_voted_menu_id).first().name
    return render_template('mealconfirm.html',menu = highest_voted_menu)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#other functions
def get_restaurant_and_menus():
    restaurants = Restaurant.query.all()
    highest_voted_menu = current_menu()
    all_menus = {}
    for restaurant in restaurants:
        menus = Menu.query.filter_by(restaurant_id=restaurant.id).all()
        all_menus[restaurant.id] = menus
    return restaurants,all_menus,highest_voted_menu

def current_menu():
    highest_voted_menu_id = MenuHistory.query.order_by(MenuHistory.id.desc()).first()
    if highest_voted_menu_id.datetime.date() == date.today():
        highest_voted_menu = Menu.query.filter_by(id=highest_voted_menu_id.menu_id).first().name
    else:
        highest_voted_menu = Menu.query.order_by(Menu.vote.desc()).first().name
    return highest_voted_menu

def reset_votes():
    current_datetime = datetime.now()
    reset_time = current_datetime - timedelta(hours=24) 
    menus_to_reset = Menu.query.filter(Menu.date <= reset_time).all()
    for menu in menus_to_reset:
        menu.vote = 0
    db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(reset_votes, trigger='interval', hours=24)  # Run every 24 hours
scheduler.start()

if __name__ =='__main__':
    app.run(debug=True)