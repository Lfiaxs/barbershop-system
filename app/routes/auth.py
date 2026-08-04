from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash

from app import app
from app.models import Usuario, Cliente


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        usuario = Usuario.query.filter_by(
            email=email
        ).first()

        if usuario and check_password_hash(
            usuario.senha,
            senha
        ):
            session.clear()
            session["usuario"] = usuario.nome
            session["tipo"] = usuario.tipo

            return redirect(
                url_for("dashboard")
            )

        cliente = Cliente.query.filter_by(
            email=email
        ).first()

        if cliente and check_password_hash(
            cliente.senha,
            senha
        ):
            session.clear()
            session["cliente_id"] = cliente.id
            session["cliente_nome"] = cliente.nome

            return redirect(
                url_for("painel_cliente")
            )

        flash(
            "E-mail ou senha inválidos.",
            "danger"
        )
    return render_template(
        "login.html"
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        url_for("login")
    )