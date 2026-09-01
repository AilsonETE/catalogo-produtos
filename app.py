from flask import Flask, render_template
import sqlite3
app = Flask(__name__)


@app.route("/")
def index():
    conexao = sqlite3.connect("banco.db")

    categoria = conexao.execute( ' SELECT * FROM CATEGORIAS' )

    return render_template("admin/index.html", categoria = categoria)

@app.route("/produtos")
def produtos():
    return "<h1> Cadastre seu produto</h1>"


app.run(debug=True )