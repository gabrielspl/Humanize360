import flask
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
import os
import re
import uuid

from dados import candidatos, colaboradores, gestores_rh, vagas, programas
from dados import candidaturas

app = flask.Flask(__name__)
app.secret_key = "chave_secreta"

app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# ---------------- FUNÇÕES ----------------
def validar_email(email):
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(padrao, email) is not None


# ---------------- HOME ----------------

@app.route("/")
def pagina_inicial():
    return render_template("pagina_inicial.html")

@app.route("/home")
def home():
    lista_perfis = [
        {"id": 1, "nome": "Gestor"},
        {"id": 2, "nome": "Colaborador"},
        {"id": 3, "nome": "Candidato"},
    ]
    return render_template("home.html", perfis=lista_perfis)


# ---------------- PERFIS ----------------
@app.route("/perfil_colaborador")
def perfil_colaborador():
    if "colaborador_id" not in session:
        return redirect(url_for("login_colaborador"))

    colaborador = next(
        (c for c in colaboradores if c["id"] == session["colaborador_id"]),
        None
    )

    minhas_inscricoes = []
    contador_analise = 0
    
    for cand in candidaturas:
        if cand["usuario_id"] == session["colaborador_id"] and cand["tipo"] == "colaborador":
            vaga = next((v for v in vagas if v["id"] == cand["vaga_id"]), None)
            cand["vaga_nome"] = vaga["titulo"] if vaga else "Vaga Interna"
            
            if cand.get("status", "Em Análise") == "Em Análise":
                contador_analise += 1
                
            minhas_inscricoes.append(cand)

    meus_programas = [
        {"titulo": "Treinamento Python", "progresso": 100, "status": "Concluído"},
    ]

    return render_template(
        "colaborador/perfil_colaborador.html", 
        colaborador=colaborador, 
        inscricoes=minhas_inscricoes,
        total_analise=contador_analise,
        programas_treinamento=meus_programas
    )


@app.route("/perfil_candidato")
def perfil_candidato():
    if "candidato_id" not in session:
        return redirect(url_for("login_candidato"))

    candidato = next(
        (c for c in candidatos if c["id"] == session["candidato_id"]),
        None
    )

    minhas_candidaturas = []
    contador_analise = 0  # Inicia o contador

    for cand in candidaturas:
        if cand["usuario_id"] == session["candidato_id"] and cand["tipo"] == "candidato":
            vaga = next((v for v in vagas if v["id"] == cand["vaga_id"]), None)
            cand["vaga_nome"] = vaga["titulo"] if vaga else "Vaga não encontrada"
            

            contador_analise += 1 
            
            minhas_candidaturas.append(cand)
    

    return render_template(
        "candidato/perfil_candidato.html", 
        candidato=candidato, 
        candidaturas_usuario=minhas_candidaturas,
        total_analise=contador_analise,
    )



@app.route('/perfil_gestor')
def perfil_gestor():
    gestor = {
        "nome": "João",
        "email": "joao@email.com",
        "empresa": "Minha Empresa"
    }

    return render_template('gestor/perfil_gestor.html', gestor=gestor)


# ---------------- VAGAS ----------------
@app.route("/vagas_colaborador")
def pag_vagas():
    return render_template("colaborador/vagas_colaborador.html", vagas=vagas)


@app.route("/vagas_candidato")
def pag2_vagas():
    return render_template("candidato/vagas_candidato.html", vagas=vagas)


@app.route("/programas_colaborador")
def pag_programas():
    return render_template("colaborador/programas_colaborador.html", programas=programas)


# ---------------- CADASTRO ----------------
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        confirmar_senha = request.form.get("confirmar_senha")
        nome = request.form.get("nome")
        idade = request.form.get("idade")
        vaga = request.form.get("vaga")
        escolaridade = request.form.get("escolaridade")

        if not validar_email(usuario):
            flash("Email inválido!", "danger")
            return render_template("cadastro.html")

        if senha != confirmar_senha:
            flash("As senhas não coincidem!", "danger")
            return render_template("cadastro.html")

        for c in candidatos:
            if c["usuario"] == usuario:
                flash("Usuário já cadastrado!", "danger")
                return render_template("cadastro.html")

        # 🔥 CRIA COM ID (IMPORTANTE)
        novo_candidato = {
            "id": len(candidatos) + 1,
            "usuario": usuario,
            "senha": senha,
            "nome": nome,
            "idade": int(idade),
            "vaga": vaga,
            "escolaridade": escolaridade,
            "localizacao": "Não informado"
        }

        candidatos.append(novo_candidato)

        flash("Cadastro realizado com sucesso!", "success")
        return redirect(url_for("login_candidato"))

    return render_template("cadastro.html")


# ---------------- LOGIN ----------------
@app.route("/login_candidato", methods=["GET", "POST"])
def login_candidato():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        for c in candidatos:
            if c["usuario"] == usuario and c["senha"] == senha:
                session.clear()
                session["candidato_id"] = c["id"]
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for("perfil_candidato"))

        flash("Usuário ou senha inválidos!", "danger")

    return render_template("candidato/login_candidato.html")


@app.route("/login_colaborador", methods=["GET", "POST"])
def login_colaborador():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if not usuario.endswith("@humanize.com"):
            flash("O email deve ser do domínio @humanize.com", "danger")
            return redirect(url_for("login_colaborador"))

        for c in colaboradores:
            if c["usuario"] == usuario and c["senha"] == senha:
                session.clear()
                session["colaborador_id"] = c["id"]
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for("perfil_colaborador"))

        flash("Usuário ou senha inválidos!", "danger")

    return render_template("colaborador/login_colaborador.html")


@app.route("/login_gestor", methods=["GET", "POST"])
def login_gestor():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if not usuario.endswith("@humanize.com"):
            flash("O email deve ser do domínio @humanize.com", "danger")
            return redirect(url_for("login_gestor"))

        for g in gestores_rh:
            if g["usuario"] == usuario and g["senha"] == senha:
                session.clear()
                session["gestor_id"] = g["id"]
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for("perfil_gestor"))

        flash("Usuário ou senha inválidos!", "danger")

    return render_template("gestor/login_gestor.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()  # 🔥 limpa tudo
    flash("Você saiu da conta.", "info")
    return redirect(url_for("home"))


# ---------------- CANDIDATAR ----------------
@app.route("/candidatar", methods=["POST"])
def candidatar():

    usuario_id = None
    tipo = None

    # identifica quem está logado
    if "candidato_id" in session:
        usuario_id = session["candidato_id"]
        tipo = "candidato"

    elif "colaborador_id" in session:
        usuario_id = session["colaborador_id"]
        tipo = "colaborador"

    else:
        flash("Você precisa estar logado!", "danger")
        return redirect(url_for("home"))

    vaga_id = int(request.form["vaga"])

    # 🧠 novos dados do formulário
    nome = request.form["nome"]
    idade = request.form["idade"]
    escolaridade = request.form["escolaridade"]
    genero = request.form["genero"]
    cidade = request.form["cidade"]
    telefone = request.form["telefone"]

    # evitar duplicata
    existe = any(
        c["usuario_id"] == usuario_id and
        c["vaga_id"] == vaga_id and
        c["tipo"] == tipo
        for c in candidaturas
    )

    if existe:
        flash("Você já se candidatou para essa vaga!", "warning")
        return redirect(url_for("home"))

    arquivo = request.files.get("curriculo")
    nome_arquivo = ""

    if arquivo and arquivo.filename != "":
        nome_arquivo = f"{uuid.uuid4()}_{arquivo.filename}"
        caminho = os.path.join(app.config["UPLOAD_FOLDER"], nome_arquivo)
        arquivo.save(caminho)

    candidatura = {
        "usuario_id": usuario_id,
        "tipo": tipo,
        "vaga_id": vaga_id,

        # 📌 novos campos
        "nome": nome,
        "idade": idade,
        "escolaridade": escolaridade,
        "genero": genero,
        "cidade": cidade,
        "telefone": telefone,

        "curriculo": nome_arquivo
    }

    candidaturas.append(candidatura)

    flash("Candidatura enviada!", "success")

    if tipo == "candidato":
        return redirect(url_for("perfil_candidato"))
    else:
        return redirect(url_for("perfil_colaborador"))


# ---------------- GESTOR ----------------
@app.route("/gestor/candidatos")
def pag_candidatos():

    lista = []
    vagas_contador = {}

    # 🔥 PEGAR FILTROS
    filtro_genero = request.args.get("genero")
    idade_min = request.args.get("idade_min")
    idade_max = request.args.get("idade_max")
    filtro_cidade = request.args.get("cidade")
    filtro_vaga = request.args.get("vaga")

    # ❌ REMOVE ESSA LINHA (era o erro)
    # cidade = cand.get("cidade", "")

    for cand in candidaturas:

        pessoa = None

        if cand["tipo"] == "candidato":
            pessoa = next((c for c in candidatos if c["id"] == cand["usuario_id"]), None)
        elif cand["tipo"] == "colaborador":
            pessoa = next((c for c in colaboradores if c["id"] == cand["usuario_id"]), None)

        vaga = next((v for v in vagas if v["id"] == cand["vaga_id"]), None)

        if not pessoa or not vaga:
            continue

        titulo_vaga = vaga["titulo"]

        idade = int(cand.get("idade", 0))
        genero = cand.get("genero", "")
        cidade = cand.get("cidade", "")

        # 🔎 FILTROS
        if filtro_genero and genero != filtro_genero:
            continue

        if filtro_cidade:
            if normalizar(filtro_cidade) not in normalizar(cidade):
                continue

        if filtro_vaga and titulo_vaga != filtro_vaga:
            continue

        if idade_min and idade < int(idade_min):
            continue

        if idade_max and idade > int(idade_max):
            continue

        vagas_contador[titulo_vaga] = vagas_contador.get(titulo_vaga, 0) + 1

        lista.append({
            "nome": pessoa["nome"],
            "idade": idade,
            "genero": genero,
            "cidade": cidade,
            "telefone": cand.get("telefone", "Não informado"),
            "vaga": titulo_vaga,
            "vaga_id": cand["vaga_id"],
            "escolaridade": cand.get("escolaridade", "Não informado"),
            "tipo": cand["tipo"],
            "curriculo": cand["curriculo"]
        })

    return render_template(
        "gestor/candidatos.html",
        candidatos=lista,
        vagas=vagas,
        vagas_contador=vagas_contador
    )
# ---------------- DOWNLOAD ----------------
@app.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


import unicodedata

def normalizar(texto):
    if not texto:
        return ""
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return texto


@app.route("/gestor/programas")
def pag_programas_gestor():
    return render_template("gestor/programas.html", programas=programas)


@app.route("/adicionar_programa", methods=["POST"])
def adicionar_programa():

    titulo = request.form.get("titulo")
    arquivo = request.files.get("pdf")

    if not titulo:
        flash("Título obrigatório!", "danger")
        return redirect(url_for("pag_programas_gestor"))

    nome_arquivo = ""

    if arquivo and arquivo.filename.endswith(".pdf"):
        nome_arquivo = f"{uuid.uuid4()}_{arquivo.filename}"
        caminho = os.path.join(app.config["UPLOAD_FOLDER"], nome_arquivo)
        arquivo.save(caminho)
    else:
        flash("Envie um arquivo PDF válido!", "danger")
        return redirect(url_for("pag_programas_gestor"))

    novo_programa = {
        
        "titulo": titulo,
        "tipo": request.form.get("tipo"),
        "pdf": nome_arquivo
    }

    programas.append(novo_programa)

    flash("Programa adicionado com sucesso!", "success")

    return redirect(url_for("pag_programas_gestor"))