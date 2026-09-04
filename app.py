from flask import Flask, render_template
import sqlite3
app = Flask(__name__)



@app.route("/")
def index():
    return render_template("admin/index.html")

@app.route("/listar_categorias")
def listarCategorias():
    return render_template('admin/listar_categoria.html')




app.run(debug=True )