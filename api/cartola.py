from flask import Flask, render_template
from flask_cors import CORS
import aiohttp
import asyncio
import aiosqlite

app = Flask(__name__, static_url_path="/static")
CORS(app)

async def get_db():
    db = await aiosqlite.connect('cache.db')
    await db.execute('''
        CREATE TABLE IF NOT EXISTS cache (
            rodada INTEGER,
            id_time TEXT,
            pontos REAL,
            PRIMARY KEY (rodada, id_time)
        )
    ''')
    await db.commit()
    return db

@app.route("/", methods=["GET"])
def index():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    pontuacoes, totais = loop.run_until_complete(consultar_pontuacoes())
    id_times = ["48930150", "14652233", "47992511"]
    time_com_maior_pontuacao = max(totais, key=totais.get)
    return render_template("pontuacoes.html", rodadas=pontuacoes.keys(), id_times=id_times, pontos=pontuacoes, totais=totais, time_com_maior_pontuacao=time_com_maior_pontuacao)

async def consultar_pontuacoes():
    id_times = ["48930150", "14652233", "47992511"]
    rodada_atual = await obter_rodada_atual()

    pontuacoes = {}
    totais = {id_time: 0 for id_time in id_times}

    db = await get_db()
    async with db.execute('SELECT rodada, id_time, pontos FROM cache') as cursor:
        cache = {row[:2]: row[2] for row in await cursor.fetchall()}

    async with aiohttp.ClientSession() as session:
        for rodada in range(1, rodada_atual):
            pontuacoes[rodada] = {}
            for id_time in id_times:
                if (rodada, id_time) in cache:
                    pontos = round(cache[(rodada, id_time)], 2)
                else:
                    url = f"https://api.cartolafc.globo.com/time/id/{id_time}/{rodada}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            pontos = data["pontos"]
                            pontos = round(pontos, 2)
                            await db.execute('INSERT INTO cache (rodada, id_time, pontos) VALUES (?, ?, ?)', (rodada, id_time, pontos))
                            await db.commit()
                pontuacoes[rodada][id_time] = pontos
                totais[id_time] += pontos

    totais_arredondados = {id_time: round(total, 2) for id_time, total in totais.items()}
    return pontuacoes, totais_arredondados

async def obter_rodada_atual():
    url = "https://api.cartolafc.globo.com/mercado/status"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data["rodada_atual"]
            else:
                return -1

if __name__ == "__main__":
    app.run(debug=True)
