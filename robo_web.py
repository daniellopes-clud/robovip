"""
ROBO WEB MULTI-USUARIO - IQ Option
Cada usuario abre o site, digita os dados da PROPRIA conta da corretora
e o robo roda em sessao propria no servidor.
"""

import time
import threading
import datetime
import secrets
from flask import Flask, render_template_string, jsonify, request, session, redirect

from estrategia import analisar
from gestao_risco import GestaoRisco

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Sessoes de usuarios em memoria (nada e salvo em disco)
usuarios = {}

TELA = """<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Meu Robo - Automacao IQ Option</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',Arial,sans-serif}
body{background:#0d1117;color:#e6edf3;padding:20px}
.container{max-width:600px;margin:0 auto}
h1{color:#58a6ff;text-align:center;margin-bottom:6px}
.sub{text-align:center;color:#8b949e;font-size:13px;margin-bottom:25px}
.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:22px;margin-bottom:16px}
input,select{width:100%;padding:12px;margin:6px 0 14px;background:#0d1117;border:1px solid #30363d;border-radius:8px;color:#e6edf3;font-size:15px}
label{font-size:13px;color:#8b949e}
button{width:100%;padding:14px;font-size:16px;font-weight:bold;border:none;border-radius:8px;cursor:pointer;margin-top:6px}
.verde{background:#238636;color:#fff}
.vermelho{background:#da3633;color:#fff}
button:disabled{opacity:.4}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.mini{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:12px;text-align:center}
.mini .l{font-size:11px;color:#8b949e;text-transform:uppercase}
.mini .v{font-size:20px;font-weight:bold;margin-top:4px}
.ok{color:#3fb950}.ruim{color:#f85149}
.logs{background:#010409;border:1px solid #30363d;border-radius:10px;padding:14px;height:220px;overflow-y:auto;font-family:monospace;font-size:12px;line-height:1.7;margin-top:12px}
.aviso{background:rgba(210,153,34,.1);border:1px solid #d29922;color:#d29922;border-radius:8px;padding:10px;font-size:12px;margin-bottom:16px}
</style></head><body>
<div class="container">
<h1>Meu Robo</h1>
<p class="sub">Automacao IQ Option - seus dados ficam so na memoria do servidor e nao sao salvos</p>

{% if not logado %}
<div class="aviso">⚠️ Opcoes binarias sao de alto risco. A maioria dos usuarios perde dinheiro. O robo nao garante lucro. Teste em conta DEMO primeiro.</div>
<div class="card">
  <form method="post" action="/entrar">
    <label>E-mail da corretora</label>
    <input type="email" name="email" required placeholder="seu@email.com">
    <label>Senha da corretora</label>
    <input type="password" name="senha" required placeholder="sua senha">
    <label>Conta</label>
    <select name="conta"><option value="demo">DEMO (treino - recomendado)</option><option value="real">REAL (dinheiro de verdade)</option></select>
    <label>Valor por entrada (R$)</label>
    <input type="number" name="valor" step="0.5" min="1" value="2">
    <label>Paridade</label>
    <input type="text" name="paridade" value="EURUSD">
    <label>Estrategia</label>
    <select name="estrategia">
      <option value="confluencia">Confluencia RSI + Bollinger (seletiva)</option>
      <option value="rsi_tendencia">RSI + Tendencia</option>
      <option value="rsi_simples">RSI Simples (mais entradas)</option>
      <option value="cruzamento_medias">Cruzamento de Medias</option>
      <option value="bollinger">Bandas de Bollinger</option>
      <option value="estocastico">Estocastico</option>
    </select>
    <label>Stop loss do dia (R$) - ex: -50</label>
    <input type="number" name="stop" step="1" value="-50">
    <button class="verde" type="submit">CONECTAR E INICIAR</button>
  </form>
</div>
{% else %}
<div class="aviso">⚠️ Opere por sua conta e risco. O robo nao garante lucros.</div>
<div class="grid">
  <div class="mini"><div class="l">Status</div><div class="v" id="st">-</div></div>
  <div class="mini"><div class="l">Saldo</div><div class="v" id="sd">-</div></div>
  <div class="mini"><div class="l">Resultado do dia</div><div class="v" id="rd">-</div></div>
  <div class="mini"><div class="l">Operacoes</div><div class="v" id="op">0</div></div>
</div>
<div style="margin-top:16px">
  <button class="verde" id="bi" onclick="acao('ligar')">▶ INICIAR</button>
  <button class="vermelho" id="bp" onclick="acao('desligar')" disabled>⏹ PARAR</button>
</div>
<div class="logs" id="lg">Aguardando...</div>
{% endif %}
</div>
<script>
async function atualizar(){
  try{
    const r = await fetch('/api/status'); const d = await r.json();
    const st = document.getElementById('st');
    st.textContent = d.rodando ? 'Rodando' : 'Parado';
    st.className = 'v ' + (d.rodando ? 'ok' : 'ruim');
    document.getElementById('bi').disabled = d.rodando;
    document.getElementById('bp').disabled = !d.rodando;
    if(d.saldo !== null){
      document.getElementById('sd').textContent = 'R$ ' + d.saldo.toFixed(2);
      const el = document.getElementById('rd');
      el.textContent = (d.dia>=0?'+':'') + 'R$ ' + d.dia.toFixed(2);
      el.className = 'v ' + (d.dia>=0 ? 'ok' : 'ruim');
    }
    document.getElementById('op').textContent = d.operacoes;
    document.getElementById('lg').innerHTML = d.logs.join('<br>') || 'Sem logs.';
  }catch(e){}
}
async function acao(a){
  await fetch('/api/robo',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({acao:a})});
  setTimeout(atualizar,800);
}
setInterval(atualizar, 4000); atualizar();
</script>
</body></html>"""


def log(u, msg):
    linha = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    u["logs"].append(linha)
    u["logs"] = u["logs"][-100:]
    print(linha)


def loop_usuario(u):
    while u["rodando"]:
        try:
            saldo = u["api"].get_balance()
            parar, motivo = u["risco"].deve_parar(saldo)
            if parar:
                log(u, f"🛑 {motivo}")
                u["rodando"] = False
                break

            sinal = analisar(u["api"], u["paridade"], u["timeframe"], u.get("estrategia", "confluencia"))
            if sinal:
                valor = u["risco"].valor_proxima_entrada()
                log(u, f"📈 Sinal {sinal.upper()} em {u['paridade']} | R$ {valor:.2f}")
                ok, oid = u["api"].buy(valor, u["paridade"], sinal, u["timeframe"])
                if ok:
                    time.sleep(u["timeframe"] * 60 + 5)
                    lucro = u["api"].check_win_v3(oid)
                    u["risco"].registrar_resultado(lucro)
                    u["operacoes"] += 1
                    log(u, f"{'✅' if lucro>0 else '❌'} R$ {lucro:+.2f} | Saldo: R$ {u['api'].get_balance():.2f}")
                else:
                    log(u, "⚠️ Falha na ordem.")
                    time.sleep(10)
            else:
                time.sleep(u["intervalo"])
        except Exception as e:
            log(u, f"⚠️ Erro: {e}")
            time.sleep(15)



PORTAO = """<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Acesso ao Robo</title>
<style>
body{background:#0d1117;color:#e6edf3;font-family:Arial,sans-serif;text-align:center;padding:40px 20px}
.card{max-width:480px;margin:60px auto;background:#161b22;border:1px solid #30363d;border-radius:12px;padding:32px}
.btn{display:inline-block;padding:16px 40px;font-size:17px;font-weight:bold;color:#fff;background:#238636;border-radius:8px;text-decoration:none;margin-top:20px}
.aviso{color:#d29922;font-size:13px;margin-top:20px}
</style></head><body>
<div class="card">
<h1>Acesso ao Robo</h1>
<p>Para usar o robo gratuito, crie sua conta na corretora pelo botao abaixo.</p>
<p>Depois do cadastro, volte aqui que o acesso estara liberado.</p>
<a class="btn" href="/ir">CRIAR CONTA GRATUITA</a>
<p class="aviso">⚠️ Opcoes binarias sao de alto risco. O robo nao garante lucro. Comece na conta demo.</p>
</div>
</body></html>"""


@app.route("/ir")
def ir():
    session["liberado"] = True
    return redirect("https://affiliate.iqoption.net/redir/?aff=831792&aff_model=revenue&afftrack=site")

@app.route("/")
def home():
    if not session.get("liberado"):
        return render_template_string(PORTAO)
    return render_template_string(TELA, logado=session.get("uid") in usuarios)


@app.route("/entrar", methods=["POST"])
def entrar():
    from iqoptionapi.stable_api import IQ_Option
    from config import TIMEFRAME, INTERVALO_ANALISE

    email = request.form.get("email", "").strip()
    senha = request.form.get("senha", "")
    conta = request.form.get("conta", "demo")

    api = IQ_Option(email, senha)
    api.connect()
    if not api.check_connect():
        return "Falha no login. Verifique e-mail/senha. <a href='/'>Voltar</a>"

    api.change_balance(conta)
    uid = secrets.token_hex(8)
    session["uid"] = uid
    usuarios[uid] = {
        "api": api,
        "risco": GestaoRisco(),
        "rodando": False,
        "logs": [],
        "paridade": request.form.get("paridade", "EURUSD").strip().upper(),
        "estrategia": request.form.get("estrategia", "confluencia"),
        "valor": float(request.form.get("valor", 2)),
        "stop": float(request.form.get("stop", -50)),
        "timeframe": TIMEFRAME,
        "intervalo": INTERVALO_ANALISE,
        "operacoes": 0,
    }
    u = usuarios[uid]
    u["risco"].registrar_saldo_inicial(api.get_balance())
    log(u, f"Conectado em conta {conta.upper()} | Saldo: R$ {api.get_balance():.2f}")
    return render_template_string(TELA, logado=True)


@app.route("/api/status")
def status():
    u = usuarios.get(session.get("uid"))
    if not u:
        return jsonify({"rodando": False, "saldo": None, "dia": 0, "operacoes": 0, "logs": []})
    try:
        saldo = u["api"].get_balance()
        dia = u["risco"].resultado_dia(saldo)
    except Exception:
        saldo, dia = None, 0
    return jsonify({"rodando": u["rodando"], "saldo": saldo, "dia": dia,
                    "operacoes": u["operacoes"], "logs": u["logs"][-25:]})


@app.route("/api/robo", methods=["POST"])
def robo():
    u = usuarios.get(session.get("uid"))
    if not u:
        return jsonify({"ok": False}), 403
    acao = request.get_json(force=True).get("acao")
    if acao == "ligar" and not u["rodando"]:
        u["rodando"] = True
        threading.Thread(target=loop_usuario, args=(u,), daemon=True).start()
    elif acao == "desligar":
        u["rodando"] = False
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
