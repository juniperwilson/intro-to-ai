from focus import EstadoFocus, JogoFocus
from typing import Callable
from collections import namedtuple
from jogos import Game

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



# Objetivo eh escrever uma funcao que maximiza a pontuacao no torneio
                                        # funcao que recebe JogoFocus, EstadoFocus retorna tuple descrito abaixo
def func_28(estado: EstadoFocus, jogador: Callable[[JogoFocus, EstadoFocus], tuple]):
    """
    Estado do jogo Focus:
    - 'board': dicionário {(x,y): [peças, de baixo para cima]}
    - 'reserve': {'RED': n, 'GREEN': n}
    - 'captured': {'RED': n, 'GREEN': n}
    """
    
    """
    Jogador retorna uma jogada/action/move que pode estar na formas:
    - ((x,y), direction) ex ((1,3), "up")   --  move da pos (1,3) para (1,2)
    ou 
    - ('reserve', (x,y))   -- tira da reserva de pecas e coloca na posicao (x,y)
    """
