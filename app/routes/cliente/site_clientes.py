from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash

from app import app, db
from app.models import Cliente, Servico, Agendamento
from datetime import datetime, timedelta

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro_cliente():
    if request.method == "POST":
        nome = request.form["nome"].strip()
        telefone = request.form["telefone"].strip()
        email = request.form["email"].strip().lower()
        senha = request.form["senha"]
        if len(nome) < 3:
            flash("Informe um nome válido.", "danger")
            return redirect(url_for("cadastro_cliente"))
        if len(senha) < 6:
            flash("A senha deve possuir pelo menos 6 caracteres.", "danger")
            return redirect(url_for("cadastro_cliente"))

        cliente = Cliente.query.filter_by(email=email).first()

        if cliente:
            flash("Já existe um cliente com este e-mail.", "warning")
            return redirect(url_for("cadastro_cliente"))
        novo_cliente = Cliente(
            nome=nome,
            telefone=telefone,
            email=email,
            senha=generate_password_hash(senha),
            observacoes=""
        )

        db.session.add(novo_cliente)
        db.session.commit()

        flash("Cadastro realizado com sucesso! Faça seu login.", "success")
        return redirect(url_for("login"))
    return render_template("cliente/cadastro.html")


@app.route("/cliente/painel")
def painel_cliente():
    if "cliente_id" not in session:
        return redirect(url_for("login"))
    cliente = db.session.get(
        Cliente,
        session["cliente_id"]
    )
    return render_template(
        "cliente/painel.html",
        cliente=cliente
    )

@app.route("/cliente/logout")
def logout_cliente():
    session.clear()
    return redirect(
        url_for("login")
    )

@app.route("/cliente/agendamento/novo", methods=["GET", "POST"])
def novo_agendamento_cliente():
    if "cliente_id" not in session:
        return redirect(url_for("login"))

    servicos = Servico.query.order_by(Servico.nome).all()

    if request.method == "POST":
        data = datetime.strptime(
            request.form["data"],
            "%Y-%m-%d"
        ).date()
        hora = datetime.strptime(
            request.form["hora"],
            "%H:%M"
        ).time()
        servico = Servico.query.get(request.form["servico_id"])
        novo_inicio = datetime.combine(data,hora)
        novo_fim = novo_inicio + timedelta(
            minutes=servico.duracao
        )
        agendamentos_existentes = Agendamento.query.filter_by(
            data=data,
            status= "agendado"
        ).all()
        for ag in agendamentos_existentes:
            inicio_existente = datetime.combine(
                ag.data,
                ag.hora
            )
            fim_existe = inicio_existente + timedelta(
                minutes=ag.servico.duracao
            )
            if(
                novo_inicio < fim_existe
                and novo_fim > inicio_existente
            ):
                flash(
                    "Este horário já está ocupado.",
                    "danger"
                )
                return render_template(
                    "cliente/novo_agendamento.html",
                    servico=servico
                )
        novo = Agendamento(
            cliente_id=session["cliente_id"],
            servico_id=request.form["servico_id"],
            data=data,
            hora=hora,
            observacoes=request.form["observacoes"],
            status="agendado"
        )

        db.session.add(novo)
        db.session.commit()
        flash(
            "Agendamento realizado com sucesso!",
            "success"
        )
        return redirect(
            url_for("painel_cliente")
        )

    return render_template(
        "cliente/novo_agendamento.html",
        servicos=servicos
    )

@app.route("/cliente/agendamentos")
def meus_agendamentos():

    if "cliente_id" not in session:
        return redirect(url_for("login"))
    agendamentos = Agendamento.query.filter_by(
        cliente_id=session["cliente_id"],
        status="agendado"
    ).order_by(
        Agendamento.data.desc(),
        Agendamento.hora.desc()
    ).all()

    return render_template(
        "cliente/meus_agendamentos.html",
        agendamentos=agendamentos
    )

@app.route("/cliente/agendamentos/editar/<int:id>", methods=["GET", "POST"])
def editar_agendamento_cliente(id):

    if "cliente_id" not in session:
        return redirect(url_for("login"))
    agendamento = Agendamento.query.get_or_404(id)
    if agendamento.cliente_id != session["cliente_id"]:
        flash("Acesso não permitido.", "danger")
        return redirect(url_for("meus_agendamentos"))
    servicos = Servico.query.all()

    if request.method == "POST":
        data = datetime.strptime(
            request.form["data"],
            "%Y-%m-%d"
        ).date()
        hora = datetime.strptime(
            request.form["hora"],
            "%H:%M"
        ).time()
        servico = Servico.query.get(
            request.form["servico_id"]
        )
        novo_inicio = datetime.combine(data, hora)
        novo_fim = novo_inicio + timedelta(
            minutes=servico.duracao
        )
        agendamentos_existentes = Agendamento.query.filter_by(
            data=data,
            status="agendado"
        ).all()

        for ag in agendamentos_existentes:
            if ag.id == agendamento.id:
                continue
            inicio_existente = datetime.combine(
                ag.data,
                ag.hora
            )
            fim_existente = inicio_existente + timedelta(
                minutes=ag.servico.duracao
            )
            if (
                novo_inicio < fim_existente
                and novo_fim > inicio_existente
            ):
                flash(
                    "Este horário já está ocupado.",
                    "danger"
                )

                return render_template(
                    "cliente/editar_agendamento.html",
                    agendamento=agendamento,
                    servicos=servicos
                )
        agendamento.servico_id = request.form["servico_id"]
        agendamento.data = data
        agendamento.hora = hora
        agendamento.observacoes = request.form["observacoes"]

        db.session.commit()

        flash(
            "Agendamento atualizado com sucesso!",
            "success"
        )
        return redirect(url_for("meus_agendamentos"))
    return render_template(
        "cliente/editar_agendamento.html",
        agendamento=agendamento,
        servicos=servicos
    )

@app.route("/cliente/agendamento/cancelar/<int:id>")
def cancelar_agendamento_cliente(id):
    if "cliente_id" not in session:
        return redirect(url_for("login"))
    agendamento = Agendamento.query.get_or_404(id)

    if agendamento.cliente_id != session["cliente_id"]:
        flash(
            "Você não pode cancelar este agendamento.",
            "danger"
        )
        return redirect(
            url_for("meus_agendamentos")
        )
    
    db.session.delete(agendamento)
    db.session.commit()
    flash(
        "Agendamento cancelado com sucesso.",
        "success"
    )
    return redirect(
        url_for("meus_agendamentos")
    )

@app.route("/cliente/historico")
def historico_cliente():
    if "cliente_id" not in session:
        return redirect(url_for("login"))

    data_filtro = request.args.get("data")

    if data_filtro:
        data = datetime.strptime(
            data_filtro,
            "%Y-%m-%d"
        ).date()
        historico = Agendamento.query.filter_by(
            cliente_id=session["cliente_id"],
            status="concluido",
            data=data
        ).order_by(
            Agendamento.hora.desc()
        ).all()

    else:
        historico = Agendamento.query.filter_by(
            cliente_id=session["cliente_id"],
            status="concluido"
        ).order_by(
            Agendamento.data.desc(),
            Agendamento.hora.desc()
        ).all()

    return render_template(
        "cliente/historico.html",
        historico=historico,
        data_filtro=data_filtro
    )