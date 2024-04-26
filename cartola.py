from flask import Flask, render_template
from flask_cors import CORS
import requests

app = Flask(__name__, static_url_path="/static")
CORS(app)

@app.route("/", methods=["GET"])
def index():
    pontuacoes, totais = consultar_pontuacoes()
    id_times = ["48930150", "14652233", "47992511"]
    # Antes de renderizar o template HTML, identifique o time com a maior pontuação total
    time_com_maior_pontuacao = max(totais, key=totais.get)
    # Passe essa informação para o template HTML como uma variável
    return render_template("pontuacoes.html", rodadas=pontuacoes.keys(), id_times=id_times, pontos=pontuacoes, totais=totais, time_com_maior_pontuacao=time_com_maior_pontuacao)

def consultar_pontuacoes():
    id_times = ["48930150", "14652233", "47992511"]
    rodada_atual = obter_rodada_atual()

    pontuacoes = {}  # Inicializar o dicionário de pontuações
    totais = {id_time: 0 for id_time in id_times}  # Inicializar o dicionário de totais

    for rodada in range(1, rodada_atual):
        pontuacoes[rodada] = {}
        for id_time in id_times:
            pontos = consultar_pontuacao(id_time, rodada)
            pontuacoes[rodada][id_time] = pontos  # Agrupar os pontos por id de time para cada rodada
            totais[id_time] += pontos

    # Arredondar os totais para duas casas decimais
    totais_arredondados = {id_time: round(total, 2) for id_time, total in totais.items()}

    return pontuacoes, totais_arredondados

def obter_rodada_atual():
    url = "https://api.cartolafc.globo.com/mercado/status"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["rodada_atual"]
    else:
        return -1

def consultar_pontuacao(id_time, rodada):
    url = f"https://api.cartolafc.globo.com/time/id/{id_time}/{rodada}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        pontos = data["pontos"]
        # Arredondar os pontos para duas casas decimais
        pontos_arredondados = round(pontos, 2)
        return pontos_arredondados
    else:
        return -1


if __name__ == "__main__":
    app.run(debug=True)
