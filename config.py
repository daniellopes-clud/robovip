"""
Arquivo de configuracao do robo.
ATENCAO: Nunca compartilhe este arquivo — ele contem credenciais.
"""

# ══════════ CONTA ══════════
EMAIL = "seu_email_aqui"
SENHA = "sua_senha_aqui"

# Use conta DEMO (treino) antes de arriscar dinheiro real
CONTA_DEMO = True  # True = demo (treino) | False = real

# ══════════ OPERACAO ══════════
PARIDADE_PADRAO = "EURUSD"      # paridade principal
TIMEFRAME = 1                   # tempo de expiracao em minutos
VALOR_ENTRADA = 2.0             # valor por operacao (R$)
LIMITE_CONTRATOS_ABERTOS = 1    # maximo de operacoes simultaneas

# ══════════ GESTAO DE RISCO (ESSENCIAL) ══════════
STOP_LOSS_DIARIO = -50.0        # para ao perder este valor no dia (R$)
TAKE_PROFIT_DIARIO = 100.0      # para ao lucrar este valor no dia (R$)
MARTINGALE_MAX = 0              # 0 = desativado | maximo de gales apos perda
FATOR_MARTINGALE = 2.0          # multiplicador do gale (2.0 = dobra)

# ══════════ ESTRATEGIA ══════════
PERIODO_MMA_RAPIDA = 5          # media movel rapida
PERIODO_MMA_LENTA = 20          # media movel lenta
MIN_VELAS_HISTORICO = 25        # velas necessarias p/ calcular as medias
INTERVALO_ANALISE = 30          # segundos entre cada analise
