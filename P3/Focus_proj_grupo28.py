from focus import EstadoFocus, JogoFocus
from typing import Callable
from itertools import takewhile

import copy

infinity = float('inf')

# funcao do Basicus
def func_basicus(estado,jogador) :
    clone = copy.deepcopy(estado)
    winner = clone.winner()
    
    # --- Caso terminal ---
    if winner is not None:
        return infinity if winner == jogador else -infinity

    my_pilhas = clone.dominate_piles(jogador)
    opponent = 'GREEN' if jogador == 'RED' else 'RED'
    opp_pilhas = clone.dominate_piles(opponent)
    return my_pilhas - opp_pilhas


# funcao usada como funcao de avaliacao num algoritmo alphabeta com cutoff
# estado eh o estado atual do jogo
# jogador eh a string como a cor do jogador "RED" ou "GREEN"
# retorna o valor avaliado deste estado
# Objetivo eh escrever uma funcao que maximiza a pontuacao no torneio
                                        
def func_28(estado: EstadoFocus, jogador: str) -> float:
    """
    Estado do jogo Focus:
    - 'board': dicionário {(x,y): [peças, de baixo para cima]}
    - 'reserve': {'RED': n, 'GREEN': n}
    - 'captured': {'RED': n, 'GREEN': n}
    """
    
    """
    Jogador retorna uma jogada/action/move que pode estar na formas:
    - ((x,y), direction) ex ((1,3), "up")   --  move da pos (1,3) para (1, 3 - n ) se a pilha tiver altura n
    ou 
    - ('reserve', (x,y))   -- tira da reserva de pecas e coloca na posicao (x,y)
    """

    """
    STRATEGY
    - dominate the other player by being the only player that can make a move -> control all the stacks while opponent has no pieces in reserve
    - whole stacks are moved the height of stack
    - pieces are removed from the bottom of the stack if it is taller than 3.
    - having more pieces in reserve in endgame is very important
    """



    clone = copy.deepcopy(estado)
    winner = clone.winner()
    
    # --- Caso terminal ---
    if winner is not None:
        return infinity if winner == jogador else -infinity

    stage = game_stage_28(estado)
    opponent = "GREEN" if jogador == "RED" else "RED"
    
    if stage < EARLYGAME:
        # EARLY GAME
        res_weight, pos_weight, capt_weight = EARLYRES, EARLYPOS, EARLYCAPT
    if stage < EARLYGAME + MIDGAME:
        # MID GAME
        res_weight, pos_weight, capt_weight = MIDRES, MIDPOS, MIDCAPT
    else:
        # LATE GAME
        res_weight, pos_weight, capt_weight = LATERES, LATEPOS, LATECAPT

    res_val = reserve_value_28(estado, jogador, opponent)
    pos_val = position_value_28(estado, jogador, opponent)
    capt_val = captured_value_28(estado, jogador, opponent)

    return (res_val * res_weight) + (pos_val * pos_weight) + (capt_val * capt_weight)





def game_stage_28(estado: EstadoFocus) -> float:
    """
    Function that returns an estimate of the percentage of the game that has passed according to
    the number of pieces still in play
    """
    pieces_captured = estado.captured["RED"] + estado.captured["GREEN"]
    max_pieces = 16
    return 1 - (pieces_captured/max_pieces)

def reserve_value_28(estado: EstadoFocus, jogador: str, opponent) -> float:
    """
    Function that provides a normalized estimate of the value of the player's reserve
    """
    res_plyr = estado.reserve[jogador]
    res_opp = estado.reserve[opponent]
    if res_plyr == 0 and res_opp == 0:
        return 0
    return (res_plyr - res_opp) / (res_plyr + res_opp)

def position_value_28(estado: EstadoFocus, jogador: str, opponent) -> float:
    """
    Function that provides a normalized estimate of the value of the board's position
    """
    dom_weight = 0.7
    base_weight = 0.3

    # Dominating more stacks is good
    plyr_doms = estado.dominate_piles(jogador)
    opp_doms = estado.dominate_piles(opponent)

    # Having opponents pieces on the very bottom of stacks is good and better if you control the stack
    positions = [pos for pos in estado.board if len(estado.board[pos]) > 1 ]

    opp_base_counter = 0
    for pos in positions:
        opp_base_pieces = len(list(takewhile(lambda x: x == opponent, pos)))
        if estado.top_piece(pos) == jogador:
            opp_base_counter = 2 * opp_base_pieces
        else:
            opp_base_counter = opp_base_pieces

    return (plyr_doms - opp_doms) * dom_weight + opp_base_counter * base_weight


def captured_value_28(estado: EstadoFocus, jogador: str, opponent) -> float:
    """
    Function that provides a normalized estimate of the value of the pieces captured 
    """
    capt_plyr = estado.captured[jogador]
    capt_opp = estado.captured[jogador]
    if capt_plyr == 0 and capt_opp == 0:
        return 0
    return (capt_opp - capt_plyr) / (capt_opp + capt_plyr)