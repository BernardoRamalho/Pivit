def transform_into_readable_position(position, gamestate):
    square_side = gamestate.square_side

    return (position[0] - square_side / 2) // square_side, (position[1] - square_side / 2) // square_side


def check_piece_in_space(position, players):
    if position in players[0].pieces or position in players[1].pieces:
        return True


def check_edge_square(position, square_side):
    if position[0] == square_side / 2 or position[0] == square_side * 8 - square_side / 2:
        if position[1] == square_side / 2 or position[1] == square_side * 8 - square_side / 2:
            return True


def check_enemy_piece_in_space(position, players, opponent):
    if position in players[opponent].pieces:
        return True
    return False


def check_selected_piece_exists_and_is_mine(position, players, player_nr):
    if position in players[player_nr].pieces:
        return True

    return False


def check_selected_pos_is_valid(position, players, player_nr):
    if position in players[player_nr]:
        return False
    return True


def check_valid_square(position, player, opponent):
    if position in player.pieces:
        return False
    return True


def check_x_movement(piece, mouse_x, square_side, player, opponent):
    x = piece.get_position()[0]
    y = piece.get_position()[1]
    valid_square = False
    if x > mouse_x:

        while x != mouse_x:
            x -= square_side

            if not piece.evolved:
                valid_square = not valid_square

            if x == mouse_x and (valid_square or piece.evolved):
                return check_valid_square((x, y), player, opponent)

            if check_piece_in_space((x, y), [player, opponent]):
                return False

    else:
        while x != mouse_x:
            x += square_side

            if not piece.evolved:
                valid_square = not valid_square

            if x == mouse_x and (valid_square or piece.evolved):
                return check_valid_square((x, y), player, opponent)

            if (x, y) in player.pieces or (x, y) in opponent.pieces:
                return False


def check_y_movement(piece, mouse_y, square_side, player, opponent):
    x = piece.get_position()[0]
    y = piece.get_position()[1]
    valid_square = False
    if y > mouse_y:

        while y != mouse_y:
            y -= square_side

            if not piece.evolved:
                valid_square = not valid_square

            if y == mouse_y and (valid_square or piece.evolved):
                return check_valid_square((x, y), player, opponent)

            if check_piece_in_space((x, y), [player, opponent]):
                return False

    else:
        while y != mouse_y:
            y += square_side

            if not piece.evolved:
                valid_square = not valid_square

            if y == mouse_y and (valid_square or piece.evolved):
                return check_valid_square((x, y), player, opponent)

            if (x, y) in player.pieces or (x, y) in opponent.pieces:
                return False


def generate_y_up_moves(player, opponent, piece, square_side, possible_moves):
    y = piece.position[1]
    x = piece.position[0]
    valid_square = False

    while y > square_side / 2:

        y -= square_side

        if not piece.evolved:
            valid_square = not valid_square

        if check_valid_square((x, y), player, opponent) and (valid_square or piece.evolved):
            possible_moves[piece.position].append((x, y))

        if check_piece_in_space((x, y), [player, opponent]):
            break


def generate_y_down_moves(player, opponent, piece, square_side, possible_moves):
    y = piece.position[1]
    x = piece.position[0]
    valid_square = False

    while y < 8 * square_side - square_side / 2:

        y += square_side

        if not piece.evolved:
            valid_square = not valid_square

        if check_valid_square((x, y), player, opponent) and valid_square:
            possible_moves[piece.position].append((x, y))

        if check_piece_in_space((x, y), [player, opponent]):
            break


def generate_x_left_moves(player, opponent, piece, square_side, possible_moves):
    y = piece.position[1]
    x = piece.position[0]
    valid_square = False

    while x > square_side / 2:

        x -= square_side

        if not piece.evolved:
            valid_square = not valid_square

        if check_valid_square((x, y), player, opponent) and valid_square:
            possible_moves[piece.position].append((x, y))

        if check_piece_in_space((x, y), [player, opponent]):
            break


def generate_x_right_moves(player, opponent, piece, square_side, possible_moves):
    y = piece.position[1]
    x = piece.position[0]
    valid_square = False

    while x < 8 * square_side - square_side / 2:

        x += square_side

        if not piece.evolved:
            valid_square = not valid_square

        if check_valid_square((x, y), player, opponent) and valid_square:
            possible_moves[piece.position].append((x, y))

        if check_piece_in_space((x, y), [player, opponent]):
            break


def generate_all_x_movements(player, opponent, piece, square_side, possible_moves):
    if piece.position[0] != square_side / 2:
        generate_x_left_moves(player, opponent, piece, square_side, possible_moves)
    if piece.position[0] != 8 * square_side - square_side / 2:
        generate_x_right_moves(player, opponent, piece, square_side, possible_moves)


def generate_all_y_movements(player, opponent, piece, square_side, possible_moves):
    if piece.position[1] != square_side / 2:
        generate_y_up_moves(player, opponent, piece, square_side, possible_moves)
    if piece.position[1] != 8 * square_side - square_side / 2:
        generate_y_down_moves(player, opponent, piece, square_side, possible_moves)
