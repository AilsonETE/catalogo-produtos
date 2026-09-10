from flask import Flask, render_template, redirect, request, url_for
import sqlite3
import base64
app = Flask(__name__)



@app.route("/")
def index():
    return render_template("admin/index.html")

def conexao():
   conn=  sqlite3.connect('database.db')
   return conn

@app.route("/listar_categorias")
def listarCategorias():
    conn = conexao()
    categoria = conn.execute('select * from categoria')
    return render_template('admin/listar_categoria.html',
                           categorias = categoria)

@app.route("/cadastrar_categorias", methods=['GET','POST'])
def cadastrarCategorias():    

    if request.method == 'POST':
        nome_categoria = request.form.get('nome_categoria')
        descricao = request.form.get('descricao')
        ativo = request.form.get('ativo')
        imagem = request.files.get('imagem')              
        imagem_base64 = base64.b64encode(imagem.read()).decode('utf-8')
        if nome_categoria:
            conn = conexao()
            conn.execute('''INSERT INTO categoria (nome, descricao, 
             ativo, imagem )
              VALUES (?, ?, ?, ?)''',
                (nome_categoria, descricao, ativo, imagem_base64))            
            conn.commit()
            conn.close()
            return redirect(url_for('listarCategoria'))        
       
    return render_template('admin/cadastrar_categoria.html')



app.run(debug=True, port=5005 )