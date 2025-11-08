from focus import EstadoFocus, JogoFocus
from typing import Callable
from itertools import take

import copy
import math

infinity = float('inf')

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

    opponent = "GREEN" if jogador == "RED" else "RED"