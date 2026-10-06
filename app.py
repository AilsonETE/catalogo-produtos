from pathlib import Path
import sqlite3
import uuid

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['UPLOAD_FOLDER'] = Path(app.root_path) / 'static' / 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)


def conexao():
    conn = sqlite3.connect(Path(app.root_path) / 'database.db')
    conn.row_factory = sqlite3.Row
    return conn


def extensao_permitida(nome_arquivo):
    return '.' in nome_arquivo and nome_arquivo.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def salvar_imagem(arquivo, prefixo='imagem'):
    """Salva a imagem em static/uploads e retorna o caminho relativo usado pelo url_for('static')."""
    if not arquivo or not arquivo.filename:
        return None

    nome_original = secure_filename(arquivo.filename)
    if not extensao_permitida(nome_original):
        raise ValueError('Formato de imagem não permitido. Use PNG, JPG, JPEG, GIF ou WEBP.')

    extensao = nome_original.rsplit('.', 1)[1].lower()
    nome = f'{prefixo}_{uuid.uuid4().hex}.{extensao}'
    arquivo.save(app.config['UPLOAD_FOLDER'] / nome)
    return f'uploads/{nome}'


def excluir_imagem(caminho):
    """Remove apenas arquivos armazenados em static/uploads."""
    if not caminho or not caminho.startswith('uploads/'):
        return
    arquivo = Path(app.root_path) / 'static' / caminho
    if arquivo.exists() and arquivo.is_file():
        arquivo.unlink()


@app.route('/')
def index():
    return render_template('admin/index.html')


@app.route('/listar_categorias')
def listarCategoria():
    with conexao() as conn:
        categorias = conn.execute('SELECT * FROM categoria ORDER BY id DESC').fetchall()
    return render_template('admin/listar_categoria.html', categorias=categorias)


@app.route('/cadastrar_categorias', methods=['GET', 'POST'])
def cadastrarCategoria():
    if request.method == 'POST':
        nome_categoria = request.form.get('nome_categoria', '').strip()
        descricao = request.form.get('descricao', '').strip()
        ativo = request.form.get('ativo', 'False')
        imagem = request.files.get('imagem')

        if not nome_categoria:
            flash('Informe o nome da categoria.', 'danger')
            return render_template('admin/cadastrar_categoria.html')

        try:
            caminho_imagem = salvar_imagem(imagem, 'categoria')
        except ValueError as erro:
            flash(str(erro), 'danger')
            return render_template('admin/cadastrar_categoria.html')

        with conexao() as conn:
            conn.execute(
                '''INSERT INTO categoria (nome, descricao, ativo, img)
                   VALUES (?, ?, ?, ?)''',
                (nome_categoria, descricao, ativo, caminho_imagem),
            )
            conn.commit()

        flash('Categoria cadastrada com sucesso.', 'success')
        return redirect(url_for('listarCategoria'))

    return render_template('admin/cadastrar_categoria.html')


@app.route('/editarcategoria/<int:id>', methods=['GET', 'POST'])
def editarCategoria(id):
    with conexao() as conn:
        categoria = conn.execute('SELECT * FROM categoria WHERE id = ?', (id,)).fetchone()

    if categoria is None:
        flash('Categoria não encontrada.', 'danger')
        return redirect(url_for('listarCategoria'))

    if request.method == 'POST':
        nome_categoria = request.form.get('nome_categoria', '').strip()
        descricao = request.form.get('descricao', '').strip()
        ativo = request.form.get('ativo', 'False')
        imagem = request.files.get('imagem')
        caminho_imagem = categoria['img']

        if not nome_categoria:
            flash('Informe o nome da categoria.', 'danger')
            return render_template('admin/editar_categoria.html', categoria=categoria)

        if imagem and imagem.filename:
            try:
                novo_caminho = salvar_imagem(imagem, f'categoria_{id}')
            except ValueError as erro:
                flash(str(erro), 'danger')
                return render_template('admin/editar_categoria.html', categoria=categoria)

            excluir_imagem(caminho_imagem)
            caminho_imagem = novo_caminho

        with conexao() as conn:
            conn.execute(
                '''UPDATE categoria
                   SET nome = ?, descricao = ?, ativo = ?, img = ?
                   WHERE id = ?''',
                (nome_categoria, descricao, ativo, caminho_imagem, id),
            )
            conn.commit()

        flash('Categoria atualizada com sucesso.', 'success')
        return redirect(url_for('listarCategoria'))

    return render_template('admin/editar_categoria.html', categoria=categoria)


@app.route('/excluir_categoria/<int:id>', methods=['GET', 'POST'])
def excluirCategoria(id):
    with conexao() as conn:
        categoria = conn.execute('SELECT * FROM categoria WHERE id = ?', (id,)).fetchone()

    if categoria is None:
        flash('Categoria não encontrada.', 'danger')
        return redirect(url_for('listarCategoria'))

    if request.method == 'POST':
        with conexao() as conn:
            conn.execute('DELETE FROM categoria WHERE id = ?', (id,))
            conn.commit()
        excluir_imagem(categoria['img'])
        flash('Categoria excluída com sucesso.', 'success')
        return redirect(url_for('listarCategoria'))

    return render_template('admin/excluir_categoria.html', categoria=categoria)


@app.route('/listar_produtos')
def listarProduto():
    with conexao() as conn:
        produtos = conn.execute(
            '''SELECT produto.*, categoria.nome AS categoria_nome
               FROM produto
               LEFT JOIN categoria ON categoria.id = produto.id_categoria
               ORDER BY produto.id DESC'''
        ).fetchall()
    return render_template('admin/listar_produto.html', produtos=produtos)


if __name__ == '__main__':
    app.run(debug=True, port=5005)
