"""
Gestao de risco: controle de banca, stop diario e martingale.
Esta e a parte MAIS IMPORTANTE do robo — nao opere sem ela.
"""

from config import (
    STOP_LOSS_DIARIO, TAKE_PROFIT_DIARIO,
    MARTINGALE_MAX, FATOR_MARTINGALE, VALOR_ENTRADA,
)


class GestaoRisco:
    def __init__(self):
        self.saldo_inicial = None
        self.perda_sequencial = 0
        self.operacoes_hoje = 0

    def registrar_saldo_inicial(self, saldo):
        self.saldo_inicial = saldo

    def resultado_dia(self, saldo_atual):
        if self.saldo_inicial is None:
            return 0.0
        return saldo_atual - self.saldo_inicial

    def deve_parar(self, saldo_atual):
        resultado = self.resultado_dia(saldo_atual)

        if resultado <= STOP_LOSS_DIARIO:
            return True, f"STOP LOSS atingido: R$ {resultado:.2f}"
        if resultado >= TAKE_PROFIT_DIARIO:
            return True, f"TAKE PROFIT atingido: R$ {resultado:.2f}"
        return False, ""

    def valor_proxima_entrada(self):
        if self.perda_sequencial > 0 and self.perda_sequencial <= MARTINGALE_MAX:
            valor = VALOR_ENTRADA * (FATOR_MARTINGALE ** self.perda_sequencial)
            print(f"[MARTINGALE] Perdas seguidas: {self.perda_sequencial} "
                  f"-> proxima entrada: R$ {valor:.2f}")
            return valor
        return VALOR_ENTRADA

    def registrar_resultado(self, lucro):
        self.operacoes_hoje += 1
        if lucro < 0:
            self.perda_sequencial += 1
        else:
            self.perda_sequencial = 0
