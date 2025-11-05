from focus import EstadoFocus, JogoFocus
from typing import Callable
from itertools import take

import copy
import math

infinity = float('inf')

def june_attemptTWO(estado: EstadoFocus, jogador: str) -> float:
    """
    Estado do jogo Focus:
    - 'board': dicionário {(x,y): [peças, de baixo para cima]}
    - 'reserve': {'RED': n, 'GREEN': n}
    - 'captured': {'RED': n, 'GREEN': n}
    
    Jogador retorna uma jogada/action/move que pode estar na formas:
    - ((x,y), direction) ex ((1,3), "up")   --  move da pos (1,3) para (1, 3 - n ) se a pilha tiver altura n
    ou 
    - ('reserve', (x,y))   -- tira da reserva de pecas e coloca na posicao (x,y)
    """
    clone = copy.deepcopy(estado)
    winner = clone.winner()
    
    # --- Caso terminal ---
    if winner is not None:
        return infinity if winner == jogador else -infinity

    opponent = "GREEN" if jogador == "RED" else "RED"

    res_val = reserve_two(estado, jogador, opponent)
    towers_val = towers_score(estado, jogador, opponent)
    captured_val = capture_score(estado, jogador, opponent)

    return (res_val + towers_val) * captured_val


def reserve_two(estado: EstadoFocus, jogador: str, opponent: str) -> float:
    res_plyr: int = estado.reserve[jogador]
    res_opp: int  = estado.reserve[opponent]
    res_diff: int = res_plyr - res_opp
    if res_diff >= 1:
        return 1 + math.log(res_diff, 2)
    else:
        return -10
    
def towers_score(estado: EstadoFocus, jogador: str, opponent: str) -> float:
    # Dominating more stacks is good
    plyr_doms = estado.dominate_piles(jogador)
    opp_doms = estado.dominate_piles(opponent)

    positions = [pos for pos in estado.board if len(estado.board[pos]) > 1 ]

    # for each tower
    plyr_tower_avg = 0
    opp_tower_avg = 0
    for pos in positions:

        # ideal dominated tower has top == jogador and every other piece opponents
        opp_pieces = len(list(take(lambda x: x == opponent, pos)))
        if estado.top_piece(pos) == jogador:
            plyr_tower_avg += opp_pieces / (len(pos) - 1)

        # ideal non dominated tower has every piece == opponent
        if estado.top_piece(pos) == opponent:
            opp_tower_avg += opp_pieces / len(pos)

    # average score of each type of tower, max is 1 best case for jogador
    plyr_tower_avg = plyr_tower_avg / plyr_doms
    opp_tower_avg = opp_tower_avg / opp_doms

    # strategic value of each group of towers
    plyr_tower_value = plyr_doms * plyr_tower_avg
    opp_tower_value = opp_doms - (opp_doms * opp_tower_avg)

    return plyr_tower_value - opp_tower_value



def capture_score(estado: EstadoFocus, jogador: str, opponent: str) -> float:
    # pieces of plyrs color that have been captured by the opponent
    capt_plyr = estado.captured[opponent]
    # pieces of opponents color captured by player
    capt_opp = estado.captured[jogador]
    capt_diff = capt_opp - capt_plyr
    return capt_diff