from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import re

app = Flask(__name__)
app.config['DEBUG'] = True

nome_banco = 'igreja.db'


def criar_tabela_membros():
    try:
        conexao = sqlite3.connect(nome_banco)
        cursor = conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS membros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo TEXT NOT NULL,
                data_nascimento TEXT,
                sexo TEXT,
                estado_civil TEXT,
                endereco TEXT,
                telefone TEXT,
                email TEXT,
                data_membresia TEXT,
                grupos TEXT
            )
        """)
        conexao.commit()
        print(f"Tabela 'membros' criada com sucesso em '{nome_banco}'!")
    except sqlite3.Error as erro:
        print(f"Erro ao criar tabela: {erro}")
    finally:
        if conexao:
            conexao.close()


def adicionar_membro(nome_completo, data_nascimento, sexo, estado_civil, endereco, telefone, email, data_membresia, grupos):
    try:
        conexao = sqlite3.connect(nome_banco)
        cursor = conexao.cursor()
        cursor.execute("""
            INSERT INTO membros (nome_completo, data_nascimento, sexo, estado_civil, endereco, telefone, email, data_membresia, grupos)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome_completo, data_nascimento, sexo, estado_civil, endereco, telefone, email, data_membresia, grupos))
        conexao.commit()
        print(f"Membro '{nome_completo}' adicionado com sucesso!")
        return cursor.lastrowid
    except sqlite3.Error as erro:
        print(f"Erro ao inserir membro: {erro}")
        conexao.rollback()
        return 0
    finally:
        if conexao:
            conexao.close()


def validar_email(email):
    return re.match(r"^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$", email) is not None


@app.route('/adicionar_membro', methods=['GET', 'POST'])
def adicionar_membro_route():
    criar_tabela_membros()
    if request.method == 'POST':
        nome_completo = request.form['nome_completo']
        data_nascimento = request.form['data_nascimento']
        sexo = request.form['sexo']
        estado_civil = request.form['estado_civil']
        endereco = request.form['endereco']
        telefone = request.form['telefone']
        email = request.form['email']
        data_membresia = request.form['data_membresia']
        grupos = request.form['grupos']

        mensagem_erro = ""
        if not nome_completo:
            mensagem_erro = "Nome Completo é obrigatório."
        elif not email or not validar_email(email):
            mensagem_erro = "Email inválido."

        if mensagem_erro:
            return render_template('adicionar_membro.html', mensagem_erro=mensagem_erro,
                                   nome_completo=nome_completo, data_nascimento=data_nascimento,
                                   sexo=sexo, estado_civil=estado_civil, endereco=endereco,
                                   telefone=telefone, email=email, data_membresia=data_membresia,
                                   grupos=grupos)

        novo_membro_id = adicionar_membro(nome_completo, data_nascimento, sexo, estado_civil, endereco, telefone, email, data_membresia, grupos)

        if novo_membro_id:
            return redirect(url_for('adicionar_membro_sucesso', nome_completo=nome_completo))
        else:
            return render_template('adicionar_membro.html', mensagem_erro="Erro ao adicionar membro. Por favor, tente novamente.")

    return render_template('adicionar_membro.html')


@app.route('/adicionar_membro_sucesso')
def adicionar_membro_sucesso():
    nome_completo = request.args.get('nome_completo')
    return render_template('adicionar_membro_sucesso.html', nome_completo=nome_completo)


if __name__ == '__main__':
    criar_tabela_membros()
    app.run(debug=True)