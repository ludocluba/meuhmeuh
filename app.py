from flask import Flask, render_template, redirect, url_for
from datetime import datetime
import pathlib as pl

from model.task import Task
from model.user import User
from model.login_form import LoginForm
from model.signup_form import SignupForm
from extension import db

root_dir = pl.Path(__file__).parent
db_path = root_dir / 'instance' / 'site.db'

# initialisation des databases
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db.init_app(app)

static_folder = 'static'

# variables globales (temporaire)
FIRST_NAME = ''
LAST_NAME = ''

d = {'first_name': FIRST_NAME, 'last_name': LAST_NAME, 'id': ''}


# page d'accueil
@app.route('/')
def home():
    """
       This is the welcome page
       It show you how to blabla
    """
    return render_template('home.html')


# Page d'inscription
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
       This is the signup page
       It will create your account to use this wonderfull webapp
    """
    form = SignupForm(request.form)
    if form.submit.data:
        # On récolte les données
        d['first_name'] = form.first_name.data
        d['last_name'] = form.last_name.data
        d['id'] = form.id.data
        d['password'] = form.password.data
        d['email'] = form.email.data
        with app.app_context():
            users = User.query.all()
            if users != []:
                # On vérifie que l'utilisateur n'existe pas déjà
                if d['id'] in [user.username for user in users]:
                    return '<p>Utilisateur déjà existant</p> <hr> <a href="/login">Connectez-vous !</a>'
                # On vérifie que l'email n'est pas déjà utilisé
                if d['email'] in [user.email for user in users]:
                    return '<p>Email déjà utilisé</p> <hr> <a href="/login">Connectez-vous !</a>'
            db.create_all()
            db.session.commit()
            # Si les conditions sont respectées, on crée un nouvel utilisateur
            create_user(d['id'], d['first_name'], d['last_name'], d['password'], d['email'])
        return redirect(url_for('accueil'))
    return render_template('signup.html', form=form)


# Fonction pour ajouter un utilisateur à la base de données
def create_user(id, first_name, last_name, password, email):
    user = User(username=id, first_name=first_name, last_name=last_name, password=password, email=email)
    db.session.add(user)
    db.session.commit()


# Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
       This is the signup page
       It will create your account to use this wonderfull webapp
    """
    form = LoginForm(request.form)
    if form.submit.data:
        d['id'] = form.id.data
        d['password'] = form.password.data
        d['first_name'] = User.query.filter_by(username=d['id']).first().first_name
        d['last_name'] = User.query.filter_by(username=d['id']).first().last_name
        with app.app_context():
            users = User.query.all()
            # On vérifie que l'utilisateur existe
            if d['id'] in [user.username for user in users]:
                user = User.query.filter_by(username=d['id']).first()
                # On vérifie que le mot de passe est correct
                if user.password == d['password']:
                    return redirect(url_for('accueil'))
            else:
                return '<p>Utilisateur non trouvé</p> <hr> <a href="/signup">Inscrivez-vous !</a>'
    return render_template('login.html', form=form)


# Fonction pour créer une tâche
def create_task(name, date, done=False):
    task = Task(name=name, date=date, done=done)
    db.session.add(task)
    db.session.commit()


# Permet de créer des tâches pour vérifier le fonctionnement de l'algo
with app.app_context():
    db.create_all()
    db.session.commit()
    create_task("task_test1", datetime.now().date())
    create_task("task_test2", datetime.now())


# Page d'accueil
@app.route("/accueil", methods=["GET", "POST"])
def accueil():
    current_date = datetime.now().date()
    # On récupère dans la base de données les tâches du jour
    tasks = Task.query.filter_by(date=current_date).all()
    completed_tasks = []
    if request.method == "POST":
        completed_tasks = request.form.getlist("important_tasks")
        # On marque les tâches comme faites dans la base de données
        for task in tasks:
            if str(task) in completed_tasks:
                # On retire la ligne et on la réécrit en changeant la valeur de done
                tasks.remove(task)
                Task.query.filter_by(name=task.name, date=current_date).delete()
                create_task(name=task.name, date=current_date, done=True)
        db.session.commit()
    return render_template('index_accueil.html', current_date=current_date, tasks=tasks,
                           completed_tasks=completed_tasks, name=[d['first_name'], d['last_name']])


from flask import request


# Page du calendrier
@app.route("/calendrier")
def calendrier():
    return render_template("calendrier.html")


# Page des recettes
@app.route("/recettes")
def recettes():
    return render_template("menu.html")


# Page des paramètres
@app.route("/parametres")
def parametres():
    return "<h1>Paramètres</h1> <a href='/accueil'> Accueil </a> <br> <p>ici c'est pour gérer les paramètres ;)</p> <p> genre les notifs, le mot de passe ... </p>"


app.run()
