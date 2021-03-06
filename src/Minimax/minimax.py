import sys
import copy
from heuristics import Heuristics
import time


class Minimax:

    saved_moves1 = []
    saved_moves2 = []

    def __init__(self, depth, mode1, mode2):
        self.max_depth = depth
        self.my_heuristics = Heuristics(mode1)
        self.their_heuristics = Heuristics(mode2)

    def value_gamestate(self, gamestate, player, me):

        if me:
            opponent = player % 2

            if gamestate.check_end_game():
                if gamestate.get_who_wins() == gamestate.player_turn:
                    return sys.maxsize
                else:
                    return -sys.maxsize + 1

            else:
                val = self.my_heuristics.value_my_pieces(gamestate, player - 1,
                                                      opponent) + self.my_heuristics.value_opponents_pieces(
                    gamestate, player - 1, opponent)
                return val

        else:
            opponent = player % 2

            if gamestate.check_end_game():
                if gamestate.get_who_wins() == gamestate.player_turn:
                    return sys.maxsize
                else:
                    return -sys.maxsize + 1

            else:
                val = self.their_heuristics.value_my_pieces(gamestate, player - 1,
                                                      opponent) + self.their_heuristics.value_opponents_pieces(
                    gamestate, player - 1, opponent)
                return val

    def min_alpha_beta(self, alpha, beta, depth, gamestate):
        # Caso o jogo acabe ou chegue ai fim retorna o valor do estado
        if depth == 0 or gamestate.check_end_game():
            return self.value_gamestate(gamestate, gamestate.player_turn, False)

        min_value = sys.maxsize

        # Gera todas as possiveis posições para o estado do jogo atual
        possible_positions = gamestate.generate_valid_moves(gamestate.player_turn)

        # Itera sobre essas posições e, para cada uma, cria um novo gamestate que vai ser depois avaliado
        for i in gamestate.players[gamestate.player_turn - 1].pieces.keys():
            if i in possible_positions.keys():
                for j in possible_positions[i]:
                    # Cria uma cópia do gamestate atual para mover a peça e depois calcular o seu valor
                    new_game_state = copy.deepcopy(gamestate)
                    new_game_state.move_piece(new_game_state.players[gamestate.player_turn - 1].pieces[i], j)
                    new_game_state.change_turn()

                    value = self.max_alpha_beta(alpha, beta, depth - 1, new_game_state)

                    # Se o valor do gamestate gerado for menor do que o menor valor que ele tem guardado então este
                    # passa a ser o melhor gamestate
                    if type(value) == tuple:
                        if value[0] < min_value:
                            min_value = min(min_value, value[0])
                            beta = min(beta, value[0])
                    elif value < min_value:
                        min_value = min(min_value, value)
                        beta = min(beta, value)

                    if beta <= alpha:
                        return min_value

        return min_value

    def max_alpha_beta(self, alpha, beta, depth, gamestate):
        # Caso o jogo acabe ou chegue ai fim retorna o valor do estado
        if depth == 0 or gamestate.check_end_game():
            return self.value_gamestate(gamestate, gamestate.player_turn, True)

        max_value = -sys.maxsize + 1

        best_move = []
        # Gera todas as possiveis posições para o estado do jogo atual
        possible_positions = gamestate.generate_valid_moves(gamestate.player_turn)

        # Itera sobre essas posições e, para cada uma, cria um novo gamestate que vai ser depois avaliado
        for i in gamestate.players[gamestate.player_turn - 1].pieces.keys():
            if i in possible_positions.keys():

                for j in possible_positions[i]:
                    # Cria uma cópia do gamestate atual para mover a peça e depois calcular o seu valor
                    new_game_state = copy.deepcopy(gamestate)
                    new_game_state.move_piece(new_game_state.players[gamestate.player_turn - 1].pieces[i], j)
                    new_game_state.change_turn()

                    value = self.min_alpha_beta(alpha, beta, depth - 1, new_game_state)

                    # Se o valor do gamestate gerado for maior do que o maior valor que ele tem guardado então este
                    # passa a ser o melhor gamestate
                    if value > max_value:
                        max_value = max(max_value, value)
                        best_move = [i, j]

                    alpha = max(alpha, value)

                    if beta <= alpha:
                        if gamestate.player_turn == 1:
                            self.saved_moves1.append([gamestate, best_move])
                        else:
                            self.saved_moves2.append([gamestate, best_move])
                        return max_value, best_move

        # Só vale a pena guardar caso estejamos num depth diferente ao inicial pois se não estariamos a guardar o
        # gamestate inicial
        if depth != self.max_depth:
            if gamestate.player_turn == 1:
                self.saved_moves1.append([gamestate, best_move])
            else:
                self.saved_moves2.append([gamestate, best_move])
        return max_value, best_move

    def play(self, gamestate):
        # Caso ele já tenha o gamestate guardado, então já sabe qual a melhor jogado
        if gamestate.player_turn == 1:
            for i in range(0, len(self.saved_moves1)):
                if gamestate == self.saved_moves1[i][0]:
                    time.sleep(1)
                    return self.saved_moves1[i][1]
        else:
            for i in range(0, len(self.saved_moves2)):
                if gamestate == self.saved_moves2[i][0]:
                    time.sleep(1)
                    return self.saved_moves2[i][1]

        # Se não, dá reset ao moves guardados para poupar memória
        if gamestate.player_turn == 1:
            self.saved_moves1.clear()
        if gamestate.player_turn == 2:
            self.saved_moves2.clear()

        max_value, best_move = self.max_alpha_beta(-sys.maxsize + 1, sys.maxsize, self.max_depth, gamestate)

        return best_move
