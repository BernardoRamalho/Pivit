import pygame
import movement


class Mouse:

    def __init__(self):
        self.piece = None
        self.position = pygame.mouse.get_pos()
        self.clickedPiece = False
        self.clickedValidSpace = False
        self.buttons = [0, 0, 0, 0, 1]  # Buttons 1, 2, 3, mouse_wheel roll up, mouse_wheel roll down, apple mouse
        # squeeze

    def set_position(self, new_position):
        self.position = new_position

    def button_press(self, button):
        self.buttons[button] = 1

    def button_release(self, button):
        self.buttons[button] = 0

    def transform_mouse_position(self, square_side, new_position):

        # Transforming the mouse position to the center of the square
        x_position = (new_position[0] // square_side) * square_side + square_side / 2
        y_position = (new_position[1] // square_side) * square_side + square_side / 2

        self.set_position((x_position, y_position))

    def check_piece_click(self, player):

        for i in player.pieces.values():

            if self.position[0] == i.position[0] and self.position[1] == i.position[1]:
                self.clickedPiece = True
                self.piece = i
                print("Player ", player.player_nr, "clicked piece at ", i.position)
                break

    def check_edge_square(self, square_side):
        if self.position[0] == square_side / 2 or self.position[0] == square_side * 8 - square_side / 2:
            if self.position[1] == square_side / 2 or self.position[1] == square_side * 8 - square_side / 2:
                return True

    def check_valid_square_click(self, square_side, player, opponent):
        x = self.piece.get_position()[0]
        y = self.piece.get_position()[1]

        if self.piece.direction == 'v':

            if self.position[0] != x or self.position[1] == y or abs(self.position[1] - y) % (2 * square_side) == 0:
                return False

            if movement.check_y_movement(x, y, self.position[1], square_side, player, opponent):

                if self.check_edge_square(square_side):
                    self.piece.evolve()

                player.change_piece_position(self.piece, self.position)
                return True

        elif self.piece.direction == 'h':

            if self.position[1] != y or self.position[0] == x or abs(self.position[0] - x) % (2 * square_side) == 0:
                return False

            if movement.check_x_movement(x, y, self.position[0], square_side, player, opponent):

                if self.check_edge_square(square_side):
                    print("Player ", player.player_nr, "has evolved a piece.")
                    self.piece.evolve()

                player.change_piece_position(self.piece, self.position)
                return True

        else:

            if movement.check_both_movements(x, y, self.position[0], self.position[1], square_side, player, opponent):

                if self.check_edge_square(square_side):
                    self.piece.evolve()

                player.change_piece_position(self.piece, self.position)
                return True

        return False