from datetime import date
from flask import render_template, redirect, session, url_for, flash
from app import app, db
from app.models import Agendamento, FechamentoFinanceiro

@app.route("/financeiro")
def financeiro():
    if "usuario" not in session:
        return redirect(url_for("login"))
    hoje = date.today()
    atendimentos = Agendamento.query.filter_by(
        status="concluido"
    ).order_by(
        Agendamento.data.desc()
    ).all()

    atendimentos_mes = []

    receita_hoje = 0
    receita_mes = 0
    quantidade = 0

    dias = []
    valores = []

    for atendimento in atendimentos:
        if (
            atendimento.data.month == hoje.month
            and atendimento.data.year == hoje.year
        ):
            atendimentos_mes.append(atendimento)
            valor = atendimento.servico.preco
            receita_mes += valor
            quantidade += 1
            dias.append(
                atendimento.data.strftime("%d/%m")
            )
            valores.append(valor)
            if atendimento.data == hoje:
                receita_hoje += valor

    ticket_medio = 0

    if quantidade > 0:
        ticket_medio = receita_mes / quantidade
    fechamento = FechamentoFinanceiro.query.filter_by(
        mes=hoje.month,
        ano=hoje.year
    ).first()

    return render_template(
        "admin/financeiro.html",
        atendimentos=atendimentos_mes,
        receita_hoje=receita_hoje,
        receita_mes=receita_mes,
        quantidade=quantidade,
        ticket_medio=ticket_medio,
        dias=dias,
        valores=valores,
        fechamento=fechamento
    )

@app.route("/financeiro/fechar")
def fechar_mes():
    if "usuario" not in session:
        return redirect(url_for("login"))
    hoje = date.today()
    fechamento = FechamentoFinanceiro.query.filter_by(
        mes=hoje.month,
        ano=hoje.year
    ).first()

    if fechamento:
        flash(
            "Este mês já foi fechado.",
            "warning"
        )
        return redirect(url_for("financeiro"))

    atendimentos = Agendamento.query.filter_by(
        status="concluido"
    ).all()

    receita = 0
    quantidade = 0

    for atendimento in atendimentos:
        if (
            atendimento.data.month == hoje.month
            and atendimento.data.year == hoje.year
        ):
            receita += atendimento.servico.preco
            quantidade += 1

    ticket = 0

    if quantidade > 0:
        ticket = receita / quantidade

    novo = FechamentoFinanceiro(
        mes=hoje.month,
        ano=hoje.year,
        receita=receita,
        quantidade=quantidade,
        ticket_medio=ticket
    )

    db.session.add(novo)
    db.session.commit()

    flash(
        "Mês fechado com sucesso.",
        "success"
    )
    return redirect(url_for("financeiro"))

@app.route("/financeiro/historico")
def historico_financeiro():
    if "usuario" not in session:
        return redirect(url_for("login"))
    fechamentos = FechamentoFinanceiro.query.order_by(
        FechamentoFinanceiro.ano.desc(),
        FechamentoFinanceiro.mes.desc()
    ).all()
    meses = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    }
    return render_template(
        "admin/historico_financeiro.html",
        fechamentos=fechamentos,
        meses=meses
    )