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
def listarCategoria():
    conn = conexao()
    categoria = conn.execute('select * from categoria')
    return render_template('admin/listar_categoria.html',
                           categorias = categoria)

@app.route("/cadastrar_categorias", methods=['GET','POST'])
def cadastrarCategoria():    

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



@app.route("/editarcategoria/<int:id>", methods=['GET','POST'])
def editarCategoria(id):
    conn = conexao()
    categoria = conn.execute('select * from categoria where id=?', 
                             (id,)).fetchone()
    if request.method == 'POST':
        nome_categoria = request.form.get('nome_categoria')
        descricao = request.form.get('descricao')
        ativo = request.form.get('ativo')
        imagem = request.files.get('imagem')              
        imagem_base64 = base64.b64encode(imagem.read()).decode('utf-8')
        if nome_categoria:
            conn = conexao()
            if imagem:
                conn.execute('''UPDATE categoria SET nome=?, descricao=?,
                              ativo=?,
                              imagem=? WHERE id=?''',   
                (nome_categoria, descricao, ativo, imagem_base64, id,))           
            else:
                conn.execute('''UPDATE categoria SET nome=?, descricao=?,
                              ativo=? WHERE id=?''',   
                (nome_categoria, descricao, ativo, id,)) 

            conn.commit()
            conn.close()
            return redirect(url_for('listarCategoria'))

    return render_template('admin/editar_categoria.html',
                            categoria=categoria )



app.run(debug=True, port=5005 )