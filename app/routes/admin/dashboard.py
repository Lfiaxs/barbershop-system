from datetime import date

from flask import render_template, redirect, session, url_for

from app import app
from app.models import Cliente, Servico, Agendamento


@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    hoje = date.today()
    total_clientes = Cliente.query.count()
    total_servicos = Servico.query.count()
    agendamentos_hoje = Agendamento.query.filter_by(
        data=hoje,
        status="agendado"
    ).count()
    pendentes = Agendamento.query.filter_by(
        status="agendado"
    ).count()

    receita_hoje = 0

    agendamentos = Agendamento.query.filter_by(
        data=hoje,
        status="agendado"
    ).all()
    for agendamento in agendamentos:
        receita_hoje += agendamento.servico.preco
    return render_template(
        "admin/dashboard.html",
        total_clientes=total_clientes,
        total_servicos=total_servicos,
        agendamentos_hoje=agendamentos_hoje,
        pendentes=pendentes,
        receita_hoje=receita_hoje
    )