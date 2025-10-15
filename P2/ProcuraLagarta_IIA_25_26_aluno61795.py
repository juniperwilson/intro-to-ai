from numbers import Number
from searchPlus_better import *
import copy

line1 = "= = = = = = =\n"
line2 = "= x . . . . =\n"
line3 = "= . . . = . =\n"
line4 = "= . . . = . =\n"
line5 = "= = = . = . =\n"
line6 = "= @ . . . . =\n"
line7 = "= = = = = = =\n"
grelha = line1 + line2 + line3 + line4 + line5 + line6 + line7

def manhattan(p,q):
    (x1,y1) = p
    (x2,y2) = q
    return abs(x1-x2) + abs(y1-y2)

class EstadoLagarta(dict): 

    def __hash__(self):
        body_sorted = tuple(sorted(self['body']))
        head = self['head']
        effort = self['effort']
        return hash((body_sorted, head, effort))
    
    def __lt__(self,other):
        """Um estado é sempre menor do que qualquer outro, para desempate na fila de prioridades"""
        return True

class MundoLagarta(Problem):

    def process_txt(self, grid):
        data = {'walls': set(), 'body': set()}
        lines = grid.split('\n')
        # atenção que a primeira linha é a de cima, mas queremos que essa seja
        # a linha y=len(lines)-1 e que a de baixo seja a linha y=0
        # então vamos inverter:
        lines.reverse()
        y = 0
        for row in lines[1:]: # ignora primeira linha, vazia (era a última linha)
            x = 0
            for col in row:
                if col == '=':
                    data['walls'].add((x,y))
                elif col == 'x':
                    data['apple'] = (x,y)
                elif col == '@':
                    data['head'] = (x,y)
                elif col == 'o':
                    data['body'].add((x,y))
                if col != " ":
                    x += 1
            y += 1
        data['dim'] = ((len(lines[-1])+1)//2,len(lines)-1)
        return data
    
    directions = {"E":(-1, 0), "D":(+1, 0), "C":(0, +1), "B":(0, -1)}  # ortogonals

    def __init__(self, MundoInicial=grelha, esforco_max=3):
        initialStatus = self.process_txt(MundoInicial) # process txt and convert to a dictionary
        self.initial=EstadoLagarta()
        self.initial['head']=initialStatus['head']
        self.initial['body']=initialStatus['body']
        self.initial['effort']=0
        self.goal = initialStatus['apple'] # goal position
        self.walls = initialStatus['walls'] # walls positions
        self.dim = initialStatus['dim'] # maze dimension (do not need to be squared)
        self.emax = esforco_max
        
    def actions (self, state):
        x, y = state['head'] # head position
        b = state['body'] # body
        e = state['effort'] # effort
        action_list = []

        # if lagarta has an empty space below the head, the only possible action is down:
        below_pos = (x,y-1)
        if below_pos not in self.walls and below_pos not in b:
            action_list = ['B'] # só pode ir para baixo
            return action_list
        
        # lagarta can go up if above cell is free and current effort is < max effort: 
        new_pos = (x+self.directions['C'][0],y+self.directions['C'][1])
        if new_pos not in self.walls and new_pos not in b and e < 3:
            action_list.append('C')
        
        # going left is possible if:
        # - left cell is free and supported (below there is wall or body)
        #   or
        # - left cell is free and unsupported and lagarta is not in effort
        new_pos = (x+self.directions['E'][0],y+self.directions['E'][1])
        if new_pos not in self.walls and new_pos not in b:
            if e == 0:
                action_list.append('E')
            else:
                below_pos = (new_pos[0],new_pos[1]-1)
                if below_pos in self.walls or below_pos in b:
                    action_list.append('E')
        
        # going right is possible if:
        # (same thing, but right)
        new_pos = (x+self.directions['D'][0],y+self.directions['D'][1])
        if new_pos not in self.walls and new_pos not in b:
            if e == 0:
                action_list.append('D')
            else:
                below_pos = (new_pos[0],new_pos[1]-1)
                if below_pos in self.walls or below_pos in b:
                    action_list.append('D')
            
        return sorted(action_list)
    
    def result (self, state, action):
        clone=copy.deepcopy(state)
        x, y = clone['head']
        b = clone['body']
        e = clone['effort']
        # determine new position of head:
        new_pos = (x+self.directions[action][0], y+self.directions[action][1])
        clone['head'] = new_pos
        # determine whether effort is increased:
        if action == 'C':
            clone['effort'] += 1
        # determine whether effort goes back to 0:
        if (new_pos[0],new_pos[1]-1) in self.walls or (new_pos[0],new_pos[1]-1) in b:
            clone['effort'] = 0
        # body fills previous head position:
        clone['body'].add((x,y))
        return clone
    
    def goal_test (self, state):
        return state['head'] == self.goal

    def path_cost(self, c, state1, action, state2):
        if action == 'C':
            cost_action = 3
        elif action == 'B':
            cost_action = 1
        else:
            cost_action = 2
        return c + cost_action
    
    def display (self, state):
        """Devolve a grelha em modo txt"""
        output = ""
        for y in range(self.dim[1]-1,-1,-1):
        # atenção, invertemos aqui a ordem dos y, pois para display começamos por cima    
            for x in range(self.dim[0]):
                if state['head'] == (x,y):
                    ch = "@"
                elif self.goal == (x,y):
                    ch = "x"
                elif (x,y) in self.walls:
                    ch = "="
                elif (x,y) in state['body']:
                    ch = "o"
                else:
                    ch = "."
                output += ch + " "
            output += "\n"
        return output
    
    def executa(self, state, actions_list, verbose=False):
        """Executa uma sequência de acções a partir do estado devolvendo o triplo formado pelo estado, 
        pelo custo acumulado e pelo booleano que indica se o objectivo foi ou não atingido. Se o objectivo 
        for atingido antes da sequência ser atingida, devolve-se o estado e o custo corrente.
        Há o modo verboso e o não verboso, por defeito."""
        cost = 0
        for a in actions_list:
            seg = self.result(state,a)
            cost = self.path_cost(cost,state,a,seg)
            state = seg
            obj = self.goal_test(state)
            if verbose:
                print('Ação:', a)
                print(self.display(state),end='')
                print('Custo Total:',cost)
                print('Esforço:',state['effort'])
                print('Atingido o objectivo?', obj)
                print()
            if obj:
                break
        return (state, cost, obj)

    def h_dist(self, node):
        """ """
        clone=copy.deepcopy(node.state)
        ## Satisfaz objectivo?
        if self.goal_test(clone):
            return 0
        distancia_lagarta_maca = manhattan(clone['head'],self.goal)
        return distancia_lagarta_maca













    def h_dist_costs(self, node):
        clone=copy.deepcopy(node.state)
        ## Satisfaz objectivo?
        if self.goal_test(clone):
            return 0
        x1, y1 = clone['head']
        x2, y2 = self.goal
        yDif = y1 - y2
        hCost = 2 * abs(x1 - x2)
        yCost = 3 * abs(yDif) if yDif <= 0 else abs(yDif)
        return hCost + yCost





def get_highest_novelty(boundary: list[tuple[Node, float]]):
    nodes, novelties = zip(*boundary)
    positions = [(-node.state['head'][0], -node.state['head'][1]) for node in nodes]
    return boundary[novelties.index(max(zip(novelties, positions))[0])]




def calc_novelties(nodes: list) -> list[tuple[Node, float]]:
    if (len(nodes) <= 1):
        return list(zip(nodes, [0.0]))
    distances = [[0]] * len(nodes)
    novelties = []
    for i in range(len(nodes)):
        this = nodes[i]
        others = [node for node in nodes if node != this]
        distances[i] = [manhattan(this.state['head'], other.state['head']) for other in others]
    novelties = list(map(lambda ls: sum(ls) / len(ls), distances))
    return list(zip(nodes, novelties))
    



def join_lists(n, first=[], second=[])->list[Node]:
    if (len(first) + len(second) <= n):
        first.extend(second)
        return first
    offset = len(first) - len(second) % n
    first.extend(second)
    result = first
    result[len(result) - n:]
    result[n - offset:].extend(result[:n - offset])
    return result




def graph_search_count_novelty(problem, N: int, frontier: list):
    """
    Search through the successors of a problem to find a goal.
    The argument frontier should be an empty list.
    If two paths reach a state, only use the first one.
    The node to expand should be the one with highest novelty.
    In case of ties, second criterium is the position of the head, lowest first.
    The maximum number of nodes in the frontier is N.
    The novelty of a node is measured as the average (Manhattan) distance
    between the node state and the states of all other nodes in the frontier.
    """
    expandidos=0
    frontier.append(Node(problem.initial))
    boundary = list(zip(frontier, [0.0]))
    explored = set()
    while True:
        if (len(boundary) == 0):
            break
        node, novelty = get_highest_novelty(boundary)
        expandidos += 1
        if problem.goal_test(node.state):
            return (node, expandidos)
        explored.add(node.state)
        boundaryNodes, _ = zip(*boundary)
        boundaryNodes = list(boundaryNodes)
        extension = [child for child in node.expand(problem) if child.state not in explored and child not in boundaryNodes]
        boundary.remove((node, novelty))
        boundaryNodes.remove(node)
        nodes = join_lists(N, boundaryNodes, extension)
        boundary = calc_novelties(nodes)
    return (None,expandidos)
