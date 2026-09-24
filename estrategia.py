# Motor de estrategias - auto-contido (nao depende de config.py)
RSI_PERIODO = 14
MEDIA_TENDENCIA_PERIODO = 50
MEDIA_CURTA_PERIODO = 9
MEDIA_LONGA_PERIODO = 21
BB_PERIODO = 20
BB_DESVIO = 2.0
STOCH_PERIODO = 14
STOCH_SOBREVENDA = 20
STOCH_SOBRECOMPRA = 80


def calcular_rsi(fechamentos, periodo=RSI_PERIODO):
    if len(fechamentos) < periodo + 1:
        return None
    ganhos, perdas = [], []
    for i in range(1, len(fechamentos)):
        variacao = fechamentos[i] - fechamentos[i - 1]
        ganhos.append(variacao if variacao > 0 else 0)
        perdas.append(abs(variacao) if variacao < 0 else 0)
    media_ganho = sum(ganhos[-periodo:]) / periodo
    media_perda = sum(perdas[-periodo:]) / periodo
    if media_perda == 0:
        return 100
    rs = media_ganho / media_perda
    return 100 - (100 / (1 + rs))


def calcular_media_movel(fechamentos, periodo):
    if len(fechamentos) < periodo:
        return None
    return sum(fechamentos[-periodo:]) / periodo


def calcular_serie_media_movel(fechamentos, periodo):
    serie = []
    for i in range(len(fechamentos)):
        if i + 1 < periodo:
            serie.append(None)
        else:
            serie.append(sum(fechamentos[i + 1 - periodo:i + 1]) / periodo)
    return serie


def calcular_bollinger(fechamentos, periodo, desvio):
    if len(fechamentos) < periodo:
        return None, None, None
    janela = fechamentos[-periodo:]
    media = sum(janela) / periodo
    variancia = sum((x - media) ** 2 for x in janela) / periodo
    dp = variancia ** 0.5
    return media, media + desvio * dp, media - desvio * dp


def calcular_estocastico(velas, periodo):
    if len(velas) < periodo:
        return None
    janela = velas[-periodo:]
    minimos = [v.get('min', v['close']) for v in janela]
    maximos = [v.get('max', v['close']) for v in janela]
    menor, maior = min(minimos), max(maximos)
    if maior == menor:
        return 50.0
    return (janela[-1]['close'] - menor) / (maior - menor) * 100


def calcular_serie_ema(valores, periodo):
    k = 2.0 / (periodo + 1)
    e = valores[0]
    saida = []
    for v in valores:
        e = v * k + e * (1 - k)
        saida.append(e)
    return saida


def analisar(api, paridade, timeframe, estrategia="confluencia",
             rsi_sobrevenda=35, rsi_sobrecompra=65):
    import time
    qtd = max(MEDIA_TENDENCIA_PERIODO, MEDIA_LONGA_PERIODO, BB_PERIODO, STOCH_PERIODO) + 25
    try:
        velas = api.get_candles(paridade, timeframe * 60, qtd, time.time())
    except Exception:
        return None
    if not velas or len(velas) < MEDIA_LONGA_PERIODO + 2:
        return None

    fechamentos = [v['close'] for v in velas]
    rsi = calcular_rsi(fechamentos)
    preco = fechamentos[-1]

    if estrategia == "rsi_simples":
        if rsi is None:
            return None
        if rsi <= rsi_sobrevenda:
            return "call"
        if rsi >= rsi_sobrecompra:
            return "put"

    elif estrategia == "cruzamento_medias":
        curta = calcular_serie_media_movel(fechamentos, MEDIA_CURTA_PERIODO)
        longa = calcular_serie_media_movel(fechamentos, MEDIA_LONGA_PERIODO)
        if None in (curta[-1], longa[-1], curta[-2], longa[-2]):
            return None
        if curta[-2] <= longa[-2] and curta[-1] > longa[-1]:
            return "call"
        if curta[-2] >= longa[-2] and curta[-1] < longa[-1]:
            return "put"

    elif estrategia == "bollinger":
        media, sup, inf = calcular_bollinger(fechamentos, BB_PERIODO, BB_DESVIO)
        if media is None:
            return None
        if preco <= inf:
            return "call"
        if preco >= sup:
            return "put"

    elif estrategia == "estocastico":
        stoch = calcular_estocastico(velas, STOCH_PERIODO)
        if stoch is None:
            return None
        if stoch <= STOCH_SOBREVENDA:
            return "call"
        if stoch >= STOCH_SOBRECOMPRA:
            return "put"

    elif estrategia == "confluencia":
        media, sup, inf = calcular_bollinger(fechamentos, BB_PERIODO, BB_DESVIO)
        if rsi is None or media is None:
            return None
        if rsi <= rsi_sobrevenda and preco <= inf:
            return "call"
        if rsi >= rsi_sobrecompra and preco >= sup:
            return "put"

    else:  # rsi_tendencia (padrao)
        tendencia = calcular_media_movel(fechamentos, MEDIA_TENDENCIA_PERIODO)
        if rsi is None or tendencia is None:
            return None
        if rsi <= rsi_sobrevenda and preco > tendencia:
            return "call"
        if rsi >= rsi_sobrecompra and preco < tendencia:
            return "put"

    return None
