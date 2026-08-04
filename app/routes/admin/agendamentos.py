from datetime import datetime, timedelta
from flask import (
    render_template,
    session,
    redirect,
    url_for,
    request,
    flash,
    jsonify
)
from app import app, db
from app.models import Cliente, Servico, Agendamento

@app.route("/agendamentos")
def agendamentos():
    if "usuario" not in session:
        return redirect(url_for("login"))

    data_filtro = request.args.get("data")

    if data_filtro:
        data = datetime.strptime(
            data_filtro,
            "%Y-%m-%d"
        ).date()

        agendamentos = Agendamento.query.filter_by(
            data=data,
            status= "agendado"
        ).order_by(
            Agendamento.hora
        ).all()

    else:
        agendamentos = Agendamento.query.filter_by(
            status="agendado"
        ).order_by(
            Agendamento.data,
            Agendamento.hora
        ).all()

    return render_template(
        "admin/agendamentos.html",
        agendamentos=agendamentos,
        data_filtro=data_filtro
    )


@app.route("/agendamentos/novo", methods=["GET", "POST"])
def novo_agendamento():
    if "usuario" not in session:
        return redirect(url_for("login"))
    clientes = Cliente.query.all()
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
        servico_escolhido = Servico.query.get(
            request.form["servico_id"]
        )
        novo_inicio = datetime.combine(data, hora)
        novo_fim = novo_inicio + timedelta(
            minutes=servico_escolhido.duracao
        )
        agendamentos_existentes = Agendamento.query.filter_by(
            data=data,
            status="agendado"
        ).all()
        for ag in agendamentos_existentes:
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
                    "Este horário entra em conflito com outro agendamento.",
                    "danger"
                )
                return render_template(
                    "admin/novo_agendamento.html",
                    clientes=clientes,
                    servicos=servicos
                )
        agendamento = Agendamento(
            cliente_id=request.form["cliente_id"],
            servico_id=request.form["servico_id"],
            data=data,
            hora=hora,
            observacoes=request.form["observacoes"]
        )

        db.session.add(agendamento)
        db.session.commit()

        flash(
            "Agendamento realizado com sucesso!",
            "success"
        )
        return redirect(
            url_for("agendamentos")
        )
    return render_template(
        "admin/novo_agendamento.html",
        clientes=clientes,
        servicos=servicos
    )

@app.route("/agendamentos/editar/<int:id>", methods=["GET", "POST"])
def editar_agendamento(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    agendamento = Agendamento.query.get_or_404(id)
    clientes = Cliente.query.all()
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
        servico_escolhido = Servico.query.get(
            request.form["servico_id"]
        )
        novo_inicio = datetime.combine(data, hora)
        novo_fim = novo_inicio + timedelta(
            minutes=servico_escolhido.duracao
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
                    "Este horário entra em conflito com outro agendamento.",
                    "danger"
                )

                return render_template(
                    "admin/editar_agendamento.html",
                    agendamento=agendamento,
                    clientes=clientes,
                    servicos=servicos
                )
        agendamento.cliente_id = request.form["cliente_id"]
        agendamento.servico_id = request.form["servico_id"]
        agendamento.data = data
        agendamento.hora = hora
        agendamento.observacoes = request.form["observacoes"]

        db.session.commit()
        flash(
            "Agendamento atualizado com sucesso!",
            "success"
        )
        return redirect(
            url_for("agendamentos")
        )
    return render_template(
        "admin/editar_agendamento.html",
        agendamento=agendamento,
        clientes=clientes,
        servicos=servicos
    )

@app.route("/agendamentos/concluir/<int:id>")
def concluir_agendamento(id):
    if "usuario" not in session:
        return redirect(url_for("login"))
    
    agendamento = Agendamento.query.get_or_404(id)
    agendamento.status = "concluido"

    db.session.commit()
    flash(
        "Atendimento concluído com sucesso!",
        "success"
    )
    return redirect(
        url_for("agendamentos")
    )

@app.route("/agendamentos/cancelar/<int:id>")
def cancelar_agendamento(id):
    if "usuario" not in session:
        return redirect(url_for("login"))
    agendamento = Agendamento.query.get_or_404(id)

    db.session.delete(agendamento)
    db.session.commit()

    flash(
        "Agendamento cancelado com sucesso!",
        "success"
    )
    return redirect(
        url_for("agendamentos")
    )

@app.route("/agendamentos/hoje")
def agendamentos_hoje():
    if "usuario" not in session:
        return redirect(url_for("login"))
    hoje = datetime.now().date()
    agendamentos = Agendamento.query.filter_by(
        data=hoje,
        status="agendado"
    ).order_by(
        Agendamento.hora
    ).all()
    return render_template(
        "admin/agendamentos_hoje.html",
        agendamentos=agendamentos,
        hoje=hoje
    )

@app.route("/agendamentos/horarios-disponiveis")
def horarios_disponiveis():
    data_str = request.args.get("data")

    if not data_str:
        return jsonify([])
    data = datetime.strptime(
        data_str,
        "%Y-%m-%d"
    ).date()

    horarios = []
    hora_atual = datetime.strptime("08:00", "%H:%M")
    hora_fim = datetime.strptime("18:00", "%H:%M")

    while hora_atual < hora_fim:
        horarios.append(
            hora_atual.strftime("%H:%M")
        )
        hora_atual += timedelta(minutes=30)
    agendamentos = Agendamento.query.filter_by(
        data=data,
        status="agendado"
    ).all()

    horarios_ocupados = []

    for ag in agendamentos:
        horarios_ocupados.append(
            ag.hora.strftime("%H:%M")
        )
    horarios_disponiveis = [
        horario
        for horario in horarios
        if horario not in horarios_ocupados
    ]
    return jsonify(horarios_disponiveis)

@app.route("/historico")
def historico():
    if "usuario" not in session:
        return redirect(url_for("login"))
    data_filtro = request.args.get("data")
    cliente_filtro = request.args.get("cliente", "").strip()
    historico = Agendamento.query.filter_by(
        status="concluido"
    )

    if data_filtro:
        data = datetime.strptime(
            data_filtro,
            "%Y-%m-%d"
        ).date()
        historico = historico.filter(
            Agendamento.data == data
        )
    if cliente_filtro:
        historico = historico.join(Cliente).filter(
            Cliente.nome.ilike(f"%{cliente_filtro}%")
        )
    historico = historico.order_by(
        Agendamento.data.desc(),
        Agendamento.hora.desc()
    ).all()

    return render_template(
        "admin/historico.html",
        historico=historico,
        data_filtro=data_filtro,
        cliente_filtro=cliente_filtro
    )