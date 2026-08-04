from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = "barbearia_fiais_2026"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///barbearia.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from app.routes import auth
from app.routes.admin import dashboard
from app.routes.admin import clientes
from app.routes.admin import servicos
from app.routes.admin import agendamentos
from app.routes.admin import financeiro
from app.routes.cliente import site_clientes