from collections import namedtuple
from jogos import Game


stateFocus = namedtuple('stateFocus', 'to_move, board, reserve, captured, n_jogadas')

MAX_JOGADAS = 250
MAX_ALTURA_PILHA = 3
TAMANHO_TABULEIRO = 4

# --- Função para criar o tabuleiro inicial ---
def criar_tabuleiro_inicial():
    """
    Cria o tabuleiro inicial do Focus :
    - Padrão central: alternância de blocos de GREEN/GREEN/RED/RED
    """
    board = {}

    pos_pares = [n for k in range(TAMANHO_TABULEIRO) for n in (2 + TAMANHO_TABULEIRO*k, 3 + TAMANHO_TABULEIRO*k)]
    pos_impares = [n for k in range(TAMANHO_TABULEIRO) for n in (0 + TAMANHO_TABULEIRO*k, 1 + TAMANHO_TABULEIRO*k)]
    # --- Região central 6x6 ---
    for x in range(TAMANHO_TABULEIRO):
        for y in range(TAMANHO_TABULEIRO):
            if y % 2 == 0 and (x in pos_pares):
                color = 'RED'
            elif y % 2 != 0 and (x in pos_impares):
                color = 'RED'
            elif y % 2 != 0 and (x in pos_pares):
                color = 'GREEN'
            else:
                color = 'GREEN'
            board[(x, y)] = [color]

    return board


class EstadoFocus(stateFocus):
    """
    Estado do jogo Focus:
    - 'board': dicionário {(x,y): [peças, de baixo para cima]}
    - 'reserve': {'RED': n, 'GREEN': n}
    - 'captured': {'RED': n, 'GREEN': n}
    """

    def all_positions(self):
        """Retorna a lista de todas as posições do tabuleiro."""
        positions = set()

        # tabuleiro 6x6 principal
        for y in range(0, TAMANHO_TABULEIRO):
            for x in range(0, TAMANHO_TABULEIRO):
                positions.add((x, y))

        # extensões 1x4
        for i in range(1, TAMANHO_TABULEIRO-1):
            positions.update({(-1, i), (TAMANHO_TABULEIRO, i), (i, -1), (i, TAMANHO_TABULEIRO)})

        return list(positions)

    def is_valid_position(self, pos):
        """Verifica se a posição faz parte do tabuleiro."""
        return pos in self.all_positions()

    def top_piece(self, pos):
        """Retorna a peça do topo (ou None se a casa estiver vazia)."""
        stack = self.board.get(pos)
        return stack[-1]
    
    def _new_position(self, pos, direction, steps):
        """Calcula a nova posição com base na direção e número de passos."""
        x, y = pos
        if direction == 'up': return (x, y - steps)
        if direction == 'down': return (x, y + steps)
        if direction == 'left': return (x - steps, y)
        if direction == 'right': return (x + steps, y)
        return pos

    def possible_moves(self):
        """
        Retorna todas as jogadas possíveis:
        - ((x,y), direction)
        - ('reserve', (x,y))
        """
        moves = []

        for pos, stack in self.board.items():
            if stack and stack[-1] == self.to_move:
                for direction in ['up', 'down', 'left', 'right']:
                    new_pos = self._new_position(pos, direction, len(stack))
                    if self.is_valid_position(new_pos):
                        moves.append((pos, direction))

        if self.reserve[self.to_move] > 0:
            for pos in self.all_positions():
                moves.append(('reserve', pos))

        return moves

    def next_state(self, action):
        """Executa uma jogada e retorna o novo estado."""

        board = {p: stack.copy() for p, stack in self.board.items()}
        reserve = self.reserve.copy()
        captured = self.captured.copy()

        if isinstance(action[0], tuple):  # movimento de pilha
            pos, direction = action
            stack = board[pos]
            steps = len(stack)
            new_pos = self._new_position(pos, direction, steps)

            moving_stack = stack.copy()
            del board[pos]
            board[new_pos] = board.get(new_pos, []) + moving_stack

            # Ajusta tamanho da pilha (máx 3)
            while len(board[new_pos]) > MAX_ALTURA_PILHA:
                removed = board[new_pos].pop(0)
                if removed == self.to_move:
                    reserve[self.to_move] += 1
                else:
                    captured[self.to_move] += 1

        elif action[0] == 'reserve':  # colocar peça da reserva
            _, pos = action
            board[pos] = board.get(pos, []) + [self.to_move]
            reserve[self.to_move] -= 1
            if len(board[pos]) > MAX_ALTURA_PILHA:
                removed = board[pos].pop(0)
                if removed == self.to_move:
                    reserve[self.to_move] += 1
                else:
                    captured[self.to_move] += 1

        next_player = 'GREEN' if self.to_move == 'RED' else 'RED'
        return EstadoFocus(next_player, board, reserve, captured, self.n_jogadas + 1)


    def other(self):
        return 'GREEN' if self.to_move == 'RED' else 'RED'

    def winner(self):
        """Retorna o vencedor ('RED', 'GREEN') ou None."""
        if self.n_jogadas < MAX_JOGADAS:
            return self.who_dominate()
        else:
            if self.dominate_piles('RED') > self.dominate_piles('GREEN'):
                return 'RED'
            elif self.dominate_piles('RED') < self.dominate_piles('GREEN'):
                return 'GREEN'
            return None

    def who_dominate(self):
        """Retorna o jogador que domina todas as pilhas (ou None)."""
        topos = {self.top_piece(pos) for pos in self.board}
        if len(topos) == 1:
            return topos.pop()
        return None

    def dominate_piles(self, player):
        """Conta quantas pilhas têm o topo pertencente ao jogador."""
        return sum(1 for s in self.board.values() if s and s[-1] == player)

    def dominate_pieces(self, player):
        """
        Retorna o número total de peças controladas pelo jogador,
        ou seja, todas as peças em pilhas cujo topo é do jogador.
        """
        return sum(len(stack) for stack in self.board.values() if stack and stack[-1] == player)
 
    def display(self):
        xs = [x for x, _ in self.all_positions()]
        ys = [y for _, y in self.all_positions()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        for y in range(min_y, max_y + 1):
            linha = []
            for x in range(min_x, max_x + 1):
                pos = (x, y)
                if not self.is_valid_position(pos):
                    linha.append("     ")  # fora do tabuleiro
                else:
                    stack = self.board.get(pos, [])
                    if not stack:
                        linha.append("[   ]")
                    else:
                        chars = "".join(p[0] for p in stack[-3:])
                        linha.append(f"[{chars:>3}]")
            print(f"{y:2d} |    " + "  ".join(linha))
        print("        " + "  ".join("_____" for _ in range(min_x, max_x + 1)))
        print("        " + "    ".join(f"{x:3d}" for x in range(min_x, max_x + 1)))
        


class JogoFocus(Game):
    """
    Implementação do jogo Focus (versão RED vs GREEN)
    """

    def __init__(self):
        self.initial = EstadoFocus(
            to_move='RED',
            board=criar_tabuleiro_inicial(),
            reserve={'RED': 0, 'GREEN': 0},
            captured={'RED': 0, 'GREEN': 0},
            n_jogadas=0
        )

    def actions(self, state):
        return state.possible_moves()

    def result(self, state, move):
        # print(state.who_dominate())
        return state.next_state(move)

    def utility(self, state, player):
        winner = state.winner()
        if winner is None:
            return 0
        return 1 if winner == player else -1

    def terminal_test(self, state):
        return state.winner() != None or state.n_jogadas == MAX_JOGADAS

    def to_move(self, state):
        return state.to_move

    def display(self, state):
        """Mostra o estado atual ou final do jogo Focus com estatísticas resumidas."""
        is_final = self.terminal_test(state)
        print("\n   Jogadas feitas:", state.n_jogadas)
        print("   Tabuleiro final:" if is_final else "   Tabuleiro atual:")

        # Mostra o tabuleiro
        state.display()

        # --- Jogo ainda a decorrer ---
        if not is_final:
            print(f"\n  Próximo jogador: {state.to_move}\n")

            print(f"{'  Peças na reserva:':<20}"
                f"{state.reserve[state.to_move]:<4}"
                f"({state.other()}: {state.reserve[state.other()]})")

            print(f"{'  Peças capturadas:':<20}"
                f"{state.captured[state.to_move]:<4}"
                f"({state.other()}: {state.captured[state.other()]})")

            print(f"{'  Pilhas dominadas:':<20}"
                f"{state.dominate_piles(state.to_move):<4}"
                f"({state.other()}: {state.dominate_piles(state.other())})")

        # --- Fim do jogo ---
        else:
            winner = state.winner()
            print("\n   FIM do jogo!")
            if winner is None:
                print(f"   Empate! Jogo terminado ao fim de {state.n_jogadas} jogadas")
            
            elif state.n_jogadas == MAX_JOGADAS:
                print(f"   ⚠️ Jogo terminado ao fim de {state.n_jogadas} jogadas! Ganhou {winner}! 🎉")

            else:
                print(f"   🎉 Ganhou {winner}! 🎉")
