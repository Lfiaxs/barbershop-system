from flask import render_template, request, redirect, url_for, session, flash
from app import app, db
from app.models import Cliente

@app.route("/clientes")
def clientes():
    if "usuario" not in session:
        return redirect(url_for("login"))

    clientes = Cliente.query.order_by(
        Cliente.nome
    ).all()

    return render_template(
        "admin/clientes.html",
        clientes=clientes
    )

@app.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    cliente = Cliente.query.get_or_404(id)

    if request.method == "POST":
        cliente.nome = request.form["nome"]
        cliente.telefone = request.form["telefone"]
        cliente.email = request.form["email"]
        cliente.observacoes = request.form["observacoes"]

        db.session.commit()

        flash(
            "Cliente atualizado com sucesso!",
            "success"
        )

        return redirect(
            url_for("clientes")
        )

    return render_template(
        "admin/editar_cliente.html",
        cliente=cliente
    )

@app.route("/clientes/excluir/<int:id>")
def excluir_cliente(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    cliente = Cliente.query.get_or_404(id)

    db.session.delete(cliente)
    db.session.commit()

    flash(
        "Cliente removido com sucesso!",
        "success"
    )
    return redirect(
        url_for("clientes")
    )