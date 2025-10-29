from focus import EstadoFocus, JogoFocus
from typing import Callable

                                        # funcao que recebe JogoFocus, EstadoFocus retorna tuple descrito abaixo
def func_28(estado: EstadoFocus, jogador: Callable[[JogoFocus, EstadoFocus], tuple]):
    """
    Jogador retorna uma jogada/action/move que pode estar na formas:
    - ((x,y), direction) ex ((1,3), "up")   --  move da pos (1,3) para (1,2)
    ou 
    - ('reserve', (x,y))   -- tira da reserva de pecas e coloca na posicao (x,y)
    """
