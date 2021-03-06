import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gym_pivit.envs.gui import Gui
import numpy as np
import time

# Piece names:
# Player color letter [r,R or b, B], Capped if evolved + Alignment -> Evolved Red Piece Horizontally Alligned = RH

pieces_to_ids = {
    # Red Uninvolved Pieces
    'r1': 1, 'r2': 2, 'r3': 3, 'r4': 4,
    'r5': 5, 'r6': 6, 'r7': 7, 'r8': 8,
    'r9': 9, 'r10': 10, 'r11': 11, 'r12': 12,
    # Red Envolved Pieces
    #'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4,
    #'R5': 5, 'R6': 6, 'R7': 7, 'R8': 8,
    #'R9': 9, 'R10': 10, 'R11': 11, 'R12': 12,
    # Blue Unevolved Pieces
    'b1': -1, 'b2': -2, 'b3': -3, 'b4': -4,
    'b5': -5, 'b6': -6, 'b7': -7, 'b8': -8,
    'b9': -9, 'b10': -10, 'b11': -11, 'b12': -12,
    # Blue Evolved
    #'B1': -1, 'B2': -2, 'B3': -3, 'B4': -4,
    #'B5': -5, 'B6': -6, 'B7': -7, 'B8': -8,
    #'B9': -9, 'B10': -10, 'B11': -11, 'B12': -12,
}

#{
# 'piece': piece_id,
#    'new_pos': m[1],
#    'type': 'move'
#}

RED = 0
BLUE = 1


class PivitEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    ids_to_pieces = {v: k for k, v in pieces_to_ids.items()}

    def setup(self):
        # The position in the array is equal to the id of the piece and it represents the orientation of the piece
        # v --> vertical; h --> horizontal
        # If the letter is Upper Case then the piece has evolved
        self.blueMap = ['none', 'v', 'v', 'v', 'v', 'h', 'h', 'h', 'h', 'v', 'v', 'v', 'v'] 
        self.redMap = ['none', 'v', 'v', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'v', 'v'] 

        # 8x8 board that has 0 if the spot is empty, the id of the piece that occupies it otherwise
        self.board = np.array([
                               [0, -1, 1, -2, -3, 2, -4, 0],
                               [3, 0, 0, 0, 0, 0, 0, 4],
                               [-5, 0, 0, 0, 0, 0, 0, -6],
                               [5, 0, 0, 0, 0, 0, 0, 6],
                               [7, 0, 0, 0, 0, 0, 0, 8],
                               [-7, 0, 0, 0, 0, 0, 0, -8],
                               [9, 0, 0, 0, 0, 0, 0, 10],
                               [0, -9, 11, -10, -11, 12, -12, 0]
                               ])

        self.player_turn = 1


    def __init__(self):
        # Representation of the 8x8 board game with 24 pieces with ids [-12, 12]
        self.observation_space = spaces.Box(-4, 4, (8, 8), dtype=np.int)  

        # All the possible actions: we have 11 possible piece ids (12 - 1, since we start at 0) that can be in 64 possible places
        # plus 64 places it can go with an action
        # That gives 64*11 + 64 = 64*12
        self.action_space = spaces.Discrete(64 * 65) 
        self.gui = Gui()
        return

    def step(self, action, random = False):
        # Validate action
        assert self.action_space.contains(action), "ACTION ERROR {}".format(action)

        reward = self.player_move(action, False)

        isDone = self.isDone()

        if isDone:
            winner = self.whoWon()
            if winner == self.player_turn:
                reward += 1
            else: reward -= 1
        elif random:
            self.player_turn *= -1
            move = np.random.choice(self.generate_valid_moves())
            self.player_move(self.move_to_action(move), False)

            if isDone:
                winner = self.whoWon()
                if winner == 1:
                    reward += 1
                else: reward -= 1

        self.player_turn *= -1
        

        return reward, isDone

    def reset(self):
        self.setup()
        return

    def render(self, mode='human'):
        self.gui.draw(self.board, self.redMap, self.blueMap)

        return

    def close(self):
        return


    def state_to_string(self):
        ret_str = ""
        for position, piece_id in np.ndenumerate(self.board):
            if piece_id == 0:
                ret_str += '0'
            else:
                if piece_id > 0:
                    if self.player_turn == 1: ret_str += 'f'
                    else: ret_str += 'e'
                    ret_str += self.redMap[piece_id]
                else:
                    piece_id *= -1
                    if self.player_turn == -1: ret_str += 'f'
                    else: ret_str += 'e'
                    ret_str += self.blueMap[piece_id]
        return ret_str
        
    ##########################
    # Gym Auxiliary Function #
    ##########################

    @staticmethod
    def move_to_action(move):
 
        new_pos = move['new_pos']
        pos = move['pos']
        return 64*(pos[0] * 8 + pos[1]) + (new_pos[0] * 8 + new_pos[1])

    @staticmethod
    def action_to_move(action):
        square = action % 64
        column = square % 8
        row = (square - column) // 8
        init_square = (action - square) // 64
        init_column = init_square % 8
        init_row = (init_square - init_column) // 8
        return {
            'pos': np.array([int(init_row), int(init_column)]),
            'new_pos': np.array([int(row), int(column)])
        }

    def player_move(self, action, greed):
        move = self.action_to_move(action)

        # Save move attributes for easier use
        pos = move['pos']
        piece_id = self.board[pos[0], pos[1]]
        new_pos = move['new_pos']
        reward = 0
        # Check if there is an enemy piece in the new position
        if self.check_piece_in(self.board, new_pos[0], new_pos[1]):
            self.kill(self.board[new_pos[0], new_pos[1]]) 
            reward += 0.1

        # Move the piece to the new square
        self.board[new_pos[0], new_pos[1]] = self.board[pos[0], pos[1]]
        self.board[pos[0], pos[1]] = '0'

        if self.check_piece_in_corner(new_pos[0], new_pos[1]):
            self.evolve(piece_id)
            reward += 0.2

        self.pivot(piece_id)
        
        return reward if greed else 0


    ##################
    # Logic Function #
    ##################

    # Check if a red piece can move to a square
    @staticmethod
    def check_valid_square_red(board, lin, col):
        piece_id = board[lin, col]

        # Pieces with positive ids are red 
        if piece_id > 0: return False
        return True

    # Check if a blue piece can move to a square
    @staticmethod
    def check_valid_square_blue(board, lin, col):
        piece_id = board[lin, col]

        # Pieces with negative ids are red 
        if piece_id < 0: return False
        return True

    # Check if there is a piece in a square
    @staticmethod
    def check_piece_in(board, lin, col):
        return not board[lin, col] == 0

    # Check if a piece as reach the corner
    @staticmethod
    def check_piece_in_corner(lin, col):
        return (lin == 0 and col == 0) or (lin == 0 and col == 7) or (lin == 7 and col == 7) or (lin == 7 and col == 0)

    # Check if a piece is evolved
    def check_piece_evolved(self, id):
        # If the letter in the map is upper case then the piece is evolved
        if id > 0 and (self.redMap[id] == 'H' or self.redMap[id] == 'V'): 
            return True
        elif id < 0 and (self.blueMap[id*(-1)] == 'H' or self.blueMap[id*(-1)] == 'V'): 
            return True
        return False
    
    # Checks the orientation of the piece
    def get_piece_orientation(self, id):
        if id > 0: return self.redMap[id]
        return self.blueMap[id*(-1)]

    # Inverts the orientation of the piece
    def pivot(self, piece_id):
        if piece_id > 0:
            if self.redMap[piece_id] == 'v':
                self.redMap[piece_id] = 'h'
            elif self.redMap[piece_id] == 'h':
                self.redMap[piece_id] = 'v'
            elif self.redMap[piece_id] == 'V':
                self.redMap[piece_id] = 'H'
            elif self.redMap[piece_id] == 'H':
                self.redMap[piece_id] = 'V'
        else:
            piece_id *= -1
            if self.blueMap[piece_id] == 'v':
                self.blueMap[piece_id] = 'h'
            elif self.blueMap[piece_id] == 'h':
                self.blueMap[piece_id] = 'v'
            elif self.blueMap[piece_id] == 'V':
                self.blueMap[piece_id] = 'H'
            elif self.blueMap[piece_id] == 'H':
                self.blueMap[piece_id] = 'V'
    
    # Evolves a piece
    def evolve(self, piece_id):
        if piece_id > 0:
            self.redMap[piece_id].upper()
        else:
            self.blueMap[piece_id].upper()
    
    # Removes a piece from the game
    def kill(self, piece_id):
        if piece_id > 0:
            self.redMap[piece_id] = 'none'
        else:
            self.blueMap[piece_id * -1] = 'none'

    # Checks if the game is over
    def isDone(self):

        if (not self.generate_valid_blue_moves()) or (not self.generate_valid_red_moves()): return True

        redCount = np.count_nonzero(np.array(self.redMap) == 'none')
        if redCount == len(self.redMap): return True
        blueCount = np.count_nonzero(np.array(self.blueMap) == 'none')
        if blueCount == len(self.blueMap): return True

        for redStatus, blueStatus in zip(self.redMap, self.blueMap):
            if (redStatus != 'none' and redStatus.islower()) or (blueStatus != 'none' and blueStatus.islower()) :
                return False
        return True

    def whoWon(self):

        if (not self.generate_valid_blue_moves()):
            return 1
        
        if (not self.generate_valid_red_moves()):
            return -1
        redCount = 0
        blueCount = 0
        for redStatus, blueStatus in zip(self.redMap, self.blueMap):
            if (redStatus.isupper()):
                redCount += 1
            if (blueStatus.isupper()):
                blueCount += 1

        if redCount > blueCount:
            return 1
        elif redCount < blueCount:
            return -1

        redCount = np.count_nonzero(np.array(self.redMap) == 'none')
        if redCount == len(self.redMap): return -1
        blueCount = np.count_nonzero(np.array(self.blueMap) == 'none')
        if blueCount == len(self.blueMap): return 1

        return 0

    # Searches for a piece in the board
    def get_piece_position(self, id):
        for position, piece_id in np.ndenumerate(self.board):
            if piece_id == id:
                return position

    #####################
    # Movement Function #
    #####################

    def generate_valid_moves(self):
        if self.player_turn == 1:
            return self.generate_valid_red_moves()
        else:
            return self.generate_valid_blue_moves()

    def generate_valid_red_moves(self):
        valid_moves = []
        for position, piece_id in np.ndenumerate(self.board):
            if piece_id > 0:
                if self.redMap[piece_id] == 'h' or self.redMap[piece_id] == 'H':
                    valid_moves += self.generate_valid_moves_rh(self.board, position[0], position[1])
                elif self.redMap[piece_id] != 'none':
                    valid_moves += self.generate_valid_moves_rv(self.board, position[0], position[1])
        return valid_moves
    
    def generate_valid_blue_moves(self):
        valid_moves = []
        for position, piece_id in np.ndenumerate(self.board):
            if piece_id < 0:
                piece_id *= -1
                if self.blueMap[piece_id] == 'h' or self.blueMap[piece_id] == 'H':
                    valid_moves += self.generate_valid_moves_bh(self.board, position[0], position[1])
                elif self.blueMap[piece_id] != 'none':
                    valid_moves += self.generate_valid_moves_bv(self.board, position[0], position[1])
        return valid_moves


    def generate_valid_moves_rh(self, board, lin, col):
        # Initialize arrays to store positions and moves
        valid_positions = []
        total_moves = []
        
        # Get the piece id from the board
        piece_id = board[lin, col]
        
        # Initialize variables to help navigate the board
        i = 0
        deltaCol = col + 1

        # Check Positions to the Right
        while deltaCol < 8:
            if (i % 2 == 0 or self.check_piece_evolved(piece_id)) and self.check_valid_square_red(board, lin, deltaCol):
                valid_positions.append(((lin, col), (lin, deltaCol)))

            if self.check_piece_in(board, lin, deltaCol):
                break

            i += 1
            deltaCol += 1

        # Reinitialize the variables to help navigate the board the opposite way
        deltaCol = col - 1
        i = 0
        
        # Check Positions to the Left
        while deltaCol >= 0:
            if (i % 2 == 0 or self.check_piece_evolved(piece_id)) and self.check_valid_square_red(board, lin, deltaCol):
                valid_positions.append(((lin, col), (lin, deltaCol)))

            if self.check_piece_in(board, lin, deltaCol):
                break

            i += 1
            deltaCol -= 1

        # Transforme Positions into moves
        for m in valid_positions:
            total_moves.append({
                'pos': m[0],
                'new_pos': m[1],
                'type': 'move'
            })

        return total_moves

    def generate_valid_moves_rv(self, board, lin, col):
        # Initialize arrays to store positions and moves
        valid_positions = []
        total_moves = []
        
        # Get the piece id from the board
        piece_id = board[lin, col]
        
        # Initialize variables to help navigate the board
        i = 0
        deltaLin = lin + 1

        # Check Upper Positions
        while deltaLin < 8:
            if (i % 2 == 0 or self.check_piece_evolved(piece_id)) and self.check_valid_square_red(board, deltaLin, col):
                valid_positions.append(((lin, col), (deltaLin, col)))

            if self.check_piece_in(board, deltaLin, col):
                break

            i += 1
            deltaLin += 1

        # Reinitialize the variables to help navigate the board the opposite way
        deltaLin = lin - 1
        i = 0

        # Check Down Positions
        while deltaLin >= 0:
            if (i % 2 == 0 or self.check_piece_evolved(piece_id)) and self.check_valid_square_red(board, deltaLin, col):
                valid_positions.append(((lin, col), (deltaLin, col)))

            if self.check_piece_in(board, deltaLin, col):
                break

            i += 1
            deltaLin -= 1

        # Transforme Positions into moves
        for m in valid_positions:
            total_moves.append({
                'pos': m[0],
                'new_pos': m[1],
                'type': 'move'
            })

        return total_moves

    def generate_valid_moves_bh(self, board, lin, col):
        # Initialize arrays to store positions and moves
        valid_positions = []
        total_moves = []
        
        # Get the piece id from the board
        piece_id = board[lin, col]
        
        # Initialize variables to help navigate the board
        i = 0
        deltaCol = col + 1

        # Check Positions to the Right
        while deltaCol < 8:

            if (i % 2 == 0 or self.check_piece_evolved(piece_id)) and self.check_valid_square_blue(board, lin, deltaCol):
                valid_positions.append(((lin, col), (lin, deltaCol)))

            if self.check_piece_in(board, lin, deltaCol):
                break

            i += 1
            deltaCol += 1

        # Reinitialize the variables to help navigate the board the opposite way
        deltaCol = col - 1
        i = 0

        # Check Positions to the Left
        while deltaCol >= 0:

            if (i % 2 == 0 or self.check_piece_evolved(piece_id)) and self.check_valid_square_blue(board, lin, deltaCol):
                valid_positions.append(((lin, col), (lin, deltaCol)))

            if self.check_piece_in(board, lin, deltaCol):
                break

            i += 1
            deltaCol -= 1

        # Transforme Positions into moves   
        for m in valid_positions:
            total_moves.append({
                'pos': m[0],
                'new_pos': m[1],
                'type': 'move'
            })

        return total_moves

    def generate_valid_moves_bv(self, board, lin, col):
        # Initialize arrays to store positions and moves
        valid_positions = []
        total_moves = []
        
        # Get the piece id from the board
        piece_id = board[lin, col]
        
        # Initialize variables to help navigate the board
        i = 0
        deltaLin = lin + 1

        # Check Upper Positions
        while deltaLin < 8:

            if (i % 2 == 0 or self.check_piece_evolved(piece_id)) and self.check_valid_square_blue(board, deltaLin, col):
                valid_positions.append(((lin, col), (deltaLin, col)))

            if self.check_piece_in(board, deltaLin, col):
                break

            i += 1
            deltaLin += 1

        # Reinitialize the variables to help navigate the board the opposite way
        deltaLin = lin - 1
        i = 0

        # Check Down Positions
        while deltaLin >= 0:

            if (i % 2 == 0 or self.check_piece_evolved(piece_id)) and self.check_valid_square_blue(board, deltaLin, col):
                valid_positions.append(((lin, col), (deltaLin, col)))

            if self.check_piece_in(board, deltaLin, col):
                break

            i += 1
            deltaLin -= 1

        # Transforme Positions into moves
        for m in valid_positions:
            total_moves.append({
                'pos': m[0],
                'new_pos': m[1],
                'type': 'move'
            })

        return total_moves

    