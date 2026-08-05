from flask import render_template, request, redirect, url_for, session, flash

from app import app, db
from app.models import Servico


@app.route("/servicos")
def servicos():
    if "usuario" not in session:
        return redirect(url_for("login"))
    servicos = Servico.query.order_by(
        Servico.nome
    ).all()

    return render_template(
        "admin/servicos.html",
        servicos=servicos
    )

@app.route("/servicos/novo", methods=["GET", "POST"])
def novo_servico():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        servico = Servico(
            nome=request.form["nome"],
            preco=float(request.form["preco"]),
            duracao=int(request.form["duracao"]),
            descricao=request.form.get("descricao", "").strip()
        )

        db.session.add(servico)
        db.session.commit()

        flash(
            "Serviço cadastrado com sucesso!",
            "success"
        )
        return redirect(
            url_for("servicos")
        )
    return render_template(
        "admin/novo_servico.html"
    )

@app.route("/servicos/editar/<int:id>", methods=["GET", "POST"])
def editar_servico(id):
    if "usuario" not in session:
        return redirect(url_for("login"))
    servico = Servico.query.get_or_404(id)
    if request.method == "POST":
        servico.nome = request.form["nome"]
        servico.preco = float(request.form["preco"])
        servico.duracao = int(request.form["duracao"])
        servico.descricao = request.form["descricao"]

        db.session.commit()

        flash(
            "Serviço atualizado com sucesso!",
            "success"
        )
        return redirect(
            url_for("servicos")
        )
    return render_template(
        "admin/editar_servico.html",
        servico=servico
    )

@app.route("/servicos/excluir/<int:id>")
def excluir_servico(id):
    if "usuario" not in session:
        return redirect(url_for("login"))
    servico = Servico.query.get_or_404(id)

    db.session.delete(servico)
    db.session.commit()

    flash(
        "Serviço removido com sucesso!",
        "danger"
    )
    return redirect(
        url_for("servicos")
    )