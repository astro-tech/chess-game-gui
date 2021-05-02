import tkinter as tk
from tkinter import ttk, messagebox


# from https://stackoverflow.com/questions/7001144/range-over-character-in-python
# range function for letters
def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2) + 1):
        yield chr(c)


class Chess:
    def __init__(self, master):
        self.master = master
        self.master.title('Chess Game')
        self.screen_size = (1024, 576)  # other (1024, 576)(1366, 768)(1920, 1080)
        # 2 blue edge, 50 bar and menu, 40 tray = 92
        self.master.minsize(self.screen_size[0] - 2, self.screen_size[1] - 92)
        self.master.maxsize(self.screen_size[0] - 2, self.screen_size[1] - 92)
        self.master.geometry(f'{self.screen_size[0] - 2}x{self.screen_size[1] - 92}+0+0')
        # widgets parameters
        self.canvas_widgets_color = 'grey75'
        self.abc123_color = 'grey50'
        # square parameters
        self.square_size = int(self.screen_size[1] / 10.97)  # 70 for 1366x768
        self.light_squares_color = '#fef0d6'
        self.light_squares_highlight = '#ff836b'
        self.dark_squares_color = '#7d564a'
        self.dark_squares_highlight = '#be3625'
        # piece parameters
        self.piece_size = int(self.square_size * (5 / 7))  # 50 for 1366x768
        self.light_piece_color = '#d2ac79'
        self.light_piece_highlight = '#f4541e'
        self.dark_piece_color = '#2a1510'
        self.dark_piece_highlight = '#ca2e04'
        # font parameters
        self.font_size = int(self.square_size / 3.5)  # 20 for 1366x768
        self.font_color = 'black'
        self.font_type = 'TKDefaultFont'

        self.currently_selected = tk.StringVar()
        self.start_new_game = True

        while self.start_new_game:
            self.play_game()

    def play_game(self):
        self.clear_previous_session()
        self.load_board_setup('initial_setup.txt')
        self.draw_menu()
        self.draw_4_main_canvas()
        self.draw_chess_board()
        self.draw_captured()
        self.draw_captured_pieces()
        self.draw_squares()
        self.initialize_pieces()  # draw included
        self.display_board()  # legacy backend in terminal
        self.play_dual()
        self.ask_for_new_game()

    def play_dual(self):
        while self.game_still_going:
            self.handle_turn(self.current_player)
            self.flip_player()
            self.check_if_game_still_going()

    def clear_previous_session(self):
        self.chess_board = {}
        self.captured_pieces = {}
        self.current_player = None
        self.other_player = None
        self.selected_piece = None
        self.position1 = '  '
        self.position2 = '  '
        self.game_still_going = True
        self.winner = None
        self.start_new_game = True

        for i in self.master.winfo_children():
            print('destroying' + str(i))
            i.destroy()

    def display_board(self):  # legacy backend for development purposes
        print('-----------------------------------------------')
        print('Captured black pieces: ')
        for i in range(16):
            if i != 15:
                print(self.captured_pieces['b'][i], end=' ')
            else:
                print(self.captured_pieces['b'][i])
        print('-----------------------------------------------')
        print('--|----|----|----|----|----|----|----|----|')
        for i in self.chess_board_keys:
            if i not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8']:
                if i in ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8']:
                    print(str(i)[1] + ' | ' + self.chess_board[i] + ' | ', end='')
                else:
                    print(self.chess_board[i] + ' | ', end='')
            else:
                print(self.chess_board[i] + ' | ')
                print('--|----|----|----|----|----|----|----|----|')
        for i in char_range('a', 'h'):
            if i != 'h':
                if i == 'a':
                    print('X' + ' | ' + i + '  | ', end='')
                else:
                    print(i + '  | ', end='')
            else:
                print(str(i) + '  | ')
        print('-----------------------------------------------')
        print('Captured white pieces: ')
        for i in range(16):
            if i != 15:
                print(self.captured_pieces['w'][i], end=' ')
            else:
                print(self.captured_pieces['w'][i])
        print('-----------------------------------------------')

    def load_board_setup(self, filename):
        file = open(filename, 'r')
        data = file.read().splitlines()
        for line in data[0:64]:
            (key, value) = line.split('=')
            self.chess_board[key] = value  # importing full chess board data (old generate board)
        for color in ['w', 'b']:
            self.captured_pieces[color] = []
        for line in data[65:81]:
            value = line.split('=')[1]
            self.captured_pieces['w'].append(value)  # importing captures white pieces data
        for line in data[81:97]:
            value = line.split('=')[1]
            self.captured_pieces['b'].append(value)  # importing captures black pieces data
        current_player_line = data[97]
        current_player_value = current_player_line.split('=')[1]
        self.current_player = current_player_value
        other_player_line = data[98]
        other_player_value = other_player_line.split('=')[1]
        self.other_player = other_player_value
        file.close()
        self.chess_board_keys = list(self.chess_board.keys())
        # print(self.captured_pieces)

    def draw_menu(self):
        self.master.option_add('*tearOff', False)
        self.chess_menu = tk.Menu(self.master)
        self.master['menu'] = self.chess_menu
        self.file_menu = tk.Menu(self.chess_menu)
        self.options_menu = tk.Menu(self.chess_menu)
        self.chess_menu.add_cascade(label='File', menu=self.file_menu, underline=0)
        self.chess_menu.add_cascade(label='Options', menu=self.options_menu, underline=0)
        self.file_menu.add_command(label='New Game', command=self.new_game)
        self.file_menu.add_command(label='Load Game')
        self.file_menu.add_command(label='Save Game')
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', command=self.exit_game)
        self.options_menu.add_command(label='Board size')

    def new_game(self):
        new_response = tk.messagebox.askyesno(title='New game', message='Do you want to start new game?')
        if new_response:
            self.game_still_going = False
            self.currently_selected.set('exit')
            print('Setting up new game')

    def exit_game(self):
        exit_response = tk.messagebox.askyesno(title='Quit game', message='Do you want to exit game?')
        if exit_response:
            self.start_new_game = False
            self.game_still_going = False
            self.currently_selected.set('exit')
            print('Exiting chess')
            self.master.destroy()

    def draw_4_main_canvas(self):
        self.c_left_side = self.screen_size[1] - 100  # 92 plus 3 + 5
        self.c_right_width = self.screen_size[0] - self.c_left_side - 24  # 2blue edge,12separator, 5,5 pad x
        self.c_right_center_height = self.c_left_side / 4
        self.c_right_top_height = (self.c_left_side - self.c_right_center_height - 24) / 2  # 12 x 2 separator

        self.c_left = tk.Canvas(self.master, width=self.c_left_side, height=self.c_left_side)
        self.c_right_top = tk.Canvas(self.master, width=self.c_right_width, height=self.c_right_top_height)
        self.c_right_bottom = tk.Canvas(self.master, width=self.c_right_width, height=self.c_right_top_height)
        self.c_right_center = tk.Canvas(self.master, width=self.c_right_width, height=self.c_right_center_height)
        for canvas_item in [self.c_left, self.c_right_top, self.c_right_bottom, self.c_right_center]:
            canvas_item['bg'] = self.canvas_widgets_color
            canvas_item['highlightthickness'] = 0
        self.separator1 = ttk.Separator(self.master, orient='vertical')
        self.separator2 = ttk.Separator(self.master, orient='horizontal')
        self.separator3 = ttk.Separator(self.master, orient='horizontal')

        self.c_left.grid(column=0, row=0, columnspan=1, rowspan=5, padx=5, pady=(3, 0))
        self.separator1.grid(column=1, row=0, columnspan=1, rowspan=5, sticky='n, s')
        self.c_right_top.grid(column=2, row=0, padx=(5, 0), pady=(3, 5))
        self.separator2.grid(column=2, row=1, sticky='w, e')
        self.c_right_center.grid(column=2, row=2, padx=(5, 0), pady=5)
        self.separator3.grid(column=2, row=3, sticky='w, e')
        self.c_right_bottom.grid(column=2, row=4, padx=(5, 0), pady=(5, 0))

        self.current_player_label = self.c_right_center.create_text(
            self.c_right_width / 2, self.c_right_center_height / 2,
            text='White is next to move', fill=self.font_color,
            font=(self.font_type, self.font_size))

        self.master.bind('<Button-3>', lambda e: self.reset_selection())

    def draw_chess_board(self):
        self.c_123abc_w = (self.c_left_side - self.square_size * 8) / 2  # strip width of 1-8, a-h

        self.c_chess = tk.Canvas(self.c_left, width=self.square_size * 8, height=self.square_size * 8,
                                 bg=self.canvas_widgets_color)

        self.board_abcx2 = {}  # creating two rows of letters a-h
        for i in ['n', 's']:
            self.board_abcx2[i] = tk.Canvas(self.c_left, width=self.square_size * 8,
                                            height=self.c_123abc_w, bg=self.abc123_color)
            for j in char_range('a', 'h'):
                self.board_abcx2[i].create_text(
                    self.square_size * (ord(j) - 96.5), self.c_123abc_w / 2,
                    text=j, fill=self.font_color, font=(self.font_type, self.font_size))

        self.board_123x2 = {}  # creating two columns of numbers 1-8
        for i in ['w', 'e']:
            self.board_123x2[i] = tk.Canvas(self.c_left, width=self.c_123abc_w,
                                            height=self.c_left_side, bg=self.abc123_color)
            for j in range(0, 8):
                self.board_123x2[i].create_text(
                    self.c_123abc_w / 2, self.c_left_side - self.c_123abc_w - self.square_size * (j + 0.5),
                    text=j + 1, fill=self.font_color, font=(self.font_type, self.font_size))

        for canvas_item in [self.c_chess, self.board_abcx2['n'], self.board_abcx2['s'],
                            self.board_123x2['w'], self.board_123x2['e']]:
            canvas_item['highlightthickness'] = 0

        self.board_123x2['w'].grid(column=0, row=0, rowspan=3)
        self.board_abcx2['n'].grid(column=1, row=0)
        self.c_chess.grid(column=1, row=1)
        self.board_abcx2['s'].grid(column=1, row=2)
        self.board_123x2['e'].grid(column=2, row=0, rowspan=3)

    def draw_captured(self):
        self.c_captured = {}  # creating two areas for captured pieces
        for color, parent in [('w', self.c_right_bottom), ('b', self.c_right_top)]:
            self.c_captured[color] = tk.Canvas(parent, width=self.square_size * 8,
                                               height=self.square_size * 2, bg=self.abc123_color,
                                               highlightthickness=0)
        for color, y in [('b', self.square_size), ('w', self.c_right_top_height - self.square_size * 3)]:
            self.c_captured[color].place(anchor='n',
                                         x=self.c_right_width / 2, y=y)

        self.c_right_top.create_text(self.c_right_width / 2, self.square_size / 2,
                                     text='Captured black pieces', fill=self.font_color,
                                     font=(self.font_type, self.font_size))

        self.c_right_bottom.create_text(self.c_right_width / 2, self.c_right_top_height - self.square_size / 2,
                                        text='Captured white pieces', fill=self.font_color,
                                        font=(self.font_type, self.font_size))

    def get_captured_center(self, number):
        if number < 8:
            x = (number + 0.5) * self.square_size
            y = self.square_size * 0.5
        else:
            x = (number - 7.5) * self.square_size
            y = self.square_size * 1.5
        return x, y

    def draw_captured_pieces(self):
        for color in ['b', 'w']:
            for i in range(0, 16):
                self.c_captured[color].create_text(
                    self.get_captured_center(i),
                    text=self.txt_map_piece(self.captured_pieces[color][i][1]),
                    tag=f'captured_{str(i)}',
                    fill=self.txt_map_color(color)[0],
                    activefill=self.txt_map_color(color)[1],
                    font=(self.font_type, self.piece_size),
                    state=tk.DISABLED)
        # for i in range(1, 17):
        #     print(self.c_captured['w'].gettags(i))

    def draw_squares(self):
        for i in self.chess_board_keys:
            x0 = (ord(i[0]) - 97) * self.square_size
            y0 = abs(int(i[1]) - 8) * self.square_size
            x1 = (ord(i[0]) - 96) * self.square_size
            y1 = abs(int(i[1]) - 9) * self.square_size
            if (ord(i[0]) + int(i[1])) % 2 == 0:  # True if dark square, False if light square
                color = self.dark_squares_color
                act_color = self.dark_squares_highlight
            else:
                color = self.light_squares_color
                act_color = self.light_squares_highlight
            self.c_chess.create_rectangle(x0, y0, x1, y1, fill=color, width=0,
                                          activefill=act_color, tag=('square', 'square_' + i))
            # e not used but always created as event, so a new kw parameter n is created which is local to lambda
            self.c_chess.tag_bind('square_' + i, '<Button-1>', lambda e, n=i: self.currently_selected.set(n))

    def get_square_center(self, tag):
        x0 = self.c_chess.coords(self.c_chess.find_withtag('square_' + tag))[0]
        y0 = self.c_chess.coords(self.c_chess.find_withtag('square_' + tag))[1]
        x1 = self.c_chess.coords(self.c_chess.find_withtag('square_' + tag))[2]
        y1 = self.c_chess.coords(self.c_chess.find_withtag('square_' + tag))[3]
        xc = (x0 + x1) / 2
        yc = (y0 + y1) / 2
        return xc, yc

    def txt_map_piece(self, txt):
        if txt == 'T':
            return '♜'
        elif txt == 'f':
            return '♞'
        elif txt == 'A':
            return '♝'
        elif txt == '+':
            return '♚'
        elif txt == '*':
            return '♛'
        elif txt == 'i':
            return '♟'

    def txt_map_color(self, color):
        if color == 'w':
            return self.light_piece_color, self.light_piece_highlight
        elif color == 'b':
            return self.dark_piece_color, self.dark_piece_highlight

    def initialize_pieces(self):
        for i in self.chess_board_keys:
            if self.chess_board[i] != '  ':
                if self.chess_board[i][0] == 'w':
                    self.draw_pieces(i, 'w')
                elif self.chess_board[i][0] == 'b':
                    self.draw_pieces(i, 'b')
            # all tags has to be bound, otherwise not able to move piece after initial move
            self.c_chess.tag_bind('piece_' + i, '<Button-1>', lambda e, n=i: self.currently_selected.set(n))

    def draw_pieces(self, pos, color):
        self.c_chess.create_text(
            self.get_square_center(pos),
            text=self.txt_map_piece(self.chess_board[pos][1]),
            tag=('piece', 'piece_' + pos, color),
            fill=self.txt_map_color(color)[0],
            activefill=self.txt_map_color(color)[1],
            font=(self.font_type, self.piece_size))

    def handle_turn(self, x):
        # for i in range(1, 97):
        #     print(i, end=' ')
        #     print(self.c_chess.gettags(i))
        if x == 'w':
            print('White is next to move')
            self.c_right_center.itemconfigure(self.current_player_label, text='White is next to move')
        elif x == 'b':
            print('Black is next to move')
            self.c_right_center.itemconfigure(self.current_player_label, text='Black is next to move')

        self.c_chess.itemconfigure('piece', state=tk.DISABLED)  # initialize select piece
        self.c_chess.itemconfigure('square', state=tk.DISABLED)
        self.c_chess.itemconfigure(x, state=tk.NORMAL)
        print('waiting for position1')
        self.c_chess.wait_variable(self.currently_selected)
        if self.currently_selected.get() != 'exit':  # if user didn't close program meanwhile
            self.position1 = self.currently_selected.get()
            print('position1=' + self.position1)
            self.selected_piece = self.c_chess.find_withtag(f'piece_{self.position1}')  # get id of selected piece
            print('id=' + str(self.selected_piece))
            self.c_chess.itemconfigure(self.selected_piece, fill=self.txt_map_color(x)[1])  # set constant red

            self.c_chess.itemconfigure('piece', state=tk.DISABLED)  # initialize select square
            for i in self.generate_valid_position2(x):  # activate only valid movement squares
                self.c_chess.itemconfigure('square_' + i, state=tk.NORMAL)
            print('waiting for position2')

            # in this timeframe there's possibility to reset selection
            self.c_chess.wait_variable(self.currently_selected)

            if self.selected_piece is not None and self.currently_selected.get() != 'exit':
                self.position2 = self.currently_selected.get()
                print('position2=' + self.position2)

                if not self.virtual_move_results_check(x):
                    # if capture happens
                    if self.chess_board[self.position2] != '  ':
                        first_empty_slot = self.captured_pieces[self.other_player].index('  ')
                        # backend, copying position2 piece to other player's captured list
                        self.captured_pieces[self.other_player][first_empty_slot] = self.chess_board[self.position2]
                        # copy captured piece to captured canvas
                        self.c_captured[self.other_player].itemconfigure(
                            self.c_captured[self.other_player].find_withtag('captured_' + str(first_empty_slot)),
                            text=self.txt_map_piece(self.chess_board[self.position2][1]))
                        # get id of captured piece
                        self.captured_piece = self.c_chess.find_withtag(f'piece_{self.position2}')
                        print('captured id=' + str(self.captured_piece))
                        # delete captured piece from chess board
                        self.c_chess.delete(self.captured_piece)

                    # backend, moving piece in the chess dictionary
                    self.chess_board[self.position2] = self.chess_board[self.position1]
                    self.chess_board[self.position1] = '  '
                    self.c_chess.coords(self.selected_piece, self.get_square_center(self.position2))  # moving piece
                    self.c_chess.itemconfigure(self.selected_piece, fill=self.txt_map_color(x)[0])  # set original color
                    print('old tags=' + str(self.c_chess.gettags(self.selected_piece)))
                    self.c_chess.itemconfigure(self.selected_piece,
                                               tag=('piece', f'piece_{self.position2}', x))  # update tag of piece
                    print('new tags=' + str(self.c_chess.gettags(self.selected_piece)))
                    self.selected_piece = None
                else:
                    tk.messagebox.showwarning(title='Illegal move',
                                              message='Movement leaves or places the king in check!')
                    self.reset_selection()
                self.display_board()

    def reset_selection(self):
        if self.selected_piece is not None:
            print('resetting selected piece')
            self.c_chess.itemconfigure(self.selected_piece, fill=self.txt_map_color(self.current_player)[0])
            self.selected_piece = None
            self.currently_selected.set('reset')  # substitute anticipated position2 with a reset flag
        else:
            print('no piece to reset')

    def flip_player(self):
        if self.currently_selected.get() != 'reset':
            if self.current_player == 'w':
                self.current_player = 'b'
                self.other_player = 'w'
            elif self.current_player == 'b':
                self.current_player = 'w'
                self.other_player = 'b'
        else:
            print('reset or check condition, not flipping player')

    def generate_valid_position2(self, x):
        valid_position2 = []
        for k in self.chess_board_keys:
            self.position2 = k
            if self.check_game_rules() and \
                    self.chess_board[self.position2] not in [x + 'T', x + 'f', x + 'A', x + '+', x + '*', x + 'i']:
                valid_position2.append(k)
        return valid_position2

    def check_game_rules(self):
        if self.chess_board[self.position1] in ['wT', 'bT']:
            return self.legal_move_rook()
        if self.chess_board[self.position1] in ['wA', 'bA']:
            return self.legal_move_bishop()
        if self.chess_board[self.position1] in ['w*', 'b*']:
            return self.legal_move_queen()
        if self.chess_board[self.position1] in ['w+', 'b+']:
            return self.legal_move_king()
        if self.chess_board[self.position1] in ['wf', 'bf']:
            return self.legal_move_knight()
        if self.chess_board[self.position1] in ['wi']:
            return self.legal_move_w_pawn()
        if self.chess_board[self.position1] in ['bi']:
            return self.legal_move_b_pawn()

    def legal_move_rook(self):
        if self.check_movement_cols_rows() and self.check_obstacle_cols_rows():
            return True
        return False

    def legal_move_bishop(self):
        if self.check_movement_diagonals() and self.check_obstacle_diagonals():
            return True
        return False

    def legal_move_queen(self):
        if (self.check_movement_cols_rows() or self.check_movement_diagonals()) \
                and (self.check_obstacle_cols_rows() or self.check_obstacle_diagonals()):
            return True
        return False

    def legal_move_king(self):
        if self.max1move_all_direction():
            return True
        return False

    def legal_move_knight(self):
        if self.movement_in_l_shape():
            return True
        return False

    def legal_move_w_pawn(self):
        if self.move_up_capture_side_up() or self.first_move_2up():
            return True
        return False

    def legal_move_b_pawn(self):
        if self.move_down_capture_side_down() or self.first_move_2down():
            return True
        return False

    # movement analysis from here
    def check_movement_cols_rows(self):
        if self.position1[0] == self.position2[0] or self.position1[1] == self.position2[1]:
            return True
        return False

    def check_movement_diagonals(self):
        if abs(ord(self.position1[0]) - ord(self.position2[0])) == \
                abs(int(self.position1[1]) - int(self.position2[1])):
            return True
        return False

    def check_obstacle_cols_rows(self):
        if self.position1[0] == self.position2[0]:
            for i in range(1, abs(int(self.position2[1]) - int(self.position1[1]))):
                if self.chess_board[self.position1[0] + str(min(int(self.position1[1]),
                                                                int(self.position2[1])) + i)] != '  ':
                    return False
            return True
        elif self.position1[1] == self.position2[1]:
            for i in range(1, abs(ord(self.position2[0]) - ord(self.position1[0]))):
                if self.chess_board[chr(min(ord(self.position1[0]),
                                            ord(self.position2[0])) + i) + self.position1[1]] != '  ':
                    return False
            return True

    def check_obstacle_diagonals(self):
        if ord(self.position1[0]) - ord(self.position2[0]) == int(self.position1[1]) - int(self.position2[1]):
            for i in range(1, abs(int(self.position2[1]) - int(self.position1[1]))):
                if self.chess_board[chr(min(ord(self.position1[0]), ord(self.position2[0])) + i) +
                                    str(min(int(self.position1[1]), int(self.position2[1])) + i)] != '  ':
                    return False
            return True
        elif ord(self.position1[0]) - ord(self.position2[0]) == (int(self.position1[1]) - int(self.position2[1])) * -1:
            for i in range(1, abs(int(self.position2[1]) - int(self.position1[1]))):
                if self.chess_board[chr(min(ord(self.position1[0]), ord(self.position2[0])) + i) +
                                    str(max(int(self.position1[1]), int(self.position2[1])) - i)] != '  ':
                    return False
            return True

    def max1move_all_direction(self):
        if abs(ord(self.position2[0]) - ord(self.position1[0])) < 2 and abs(
                int(self.position2[1]) - int(self.position1[1])) < 2:
            return True
        return False

    def movement_in_l_shape(self):
        if (abs(ord(self.position2[0]) - ord(self.position1[0])) == 1 and abs(
                int(self.position2[1]) - int(self.position1[1])) == 2) or \
                (abs(ord(self.position2[0]) - ord(self.position1[0])) == 2 and abs(
                    int(self.position2[1]) - int(self.position1[1])) == 1):
            return True
        return False

    def move_up_capture_side_up(self):
        if self.chess_board[self.position2] == '  ':
            if self.position1[0] == self.position2[0] and int(self.position1[1]) - int(self.position2[1]) == -1:
                return True
            return False
        elif self.chess_board[self.position2] != '  ':
            if abs(ord(self.position2[0]) - ord(self.position1[0])) == 1 and \
                    int(self.position1[1]) - int(self.position2[1]) == -1:
                return True
            return False

    def move_down_capture_side_down(self):
        if self.chess_board[self.position2] == '  ':
            if self.position1[0] == self.position2[0] and int(self.position1[1]) - int(self.position2[1]) == 1:
                return True
            return False
        elif self.chess_board[self.position2] != '  ':
            if abs(ord(self.position2[0]) - ord(self.position1[0])) == 1 and \
                    int(self.position1[1]) - int(self.position2[1]) == 1:
                return True
            return False

    def first_move_2up(self):
        if int(self.position1[1]) == 2 and self.chess_board[self.position2] == '  ' and \
                self.chess_board[self.position2[0] + str(3)] == '  ':
            if self.position1[0] == self.position2[0] and int(self.position1[1]) - int(self.position2[1]) == -2:
                return True
            return False

    def first_move_2down(self):
        if int(self.position1[1]) == 7 and self.chess_board[self.position2] == '  ' and \
                self.chess_board[self.position2[0] + str(6)] == '  ':
            if self.position1[0] == self.position2[0] and int(self.position1[1]) - int(self.position2[1]) == 2:
                return True
            return False

    # check analysis form here
    def virtual_move_results_check(self, x):
        chess_board_virtual = self.chess_board.copy()  # shallow copy
        chess_board_virtual[self.position2] = chess_board_virtual[self.position1]
        chess_board_virtual[self.position1] = '  '
        return self.king_in_check(x, chess_board_virtual)

    # checks if xn coordinate of x player on board is under attack from enemy and returns enemy's coordinates
    def coord_danger_from(self, xn, board, x):
        if self.coord_danger_from_rook_queen(xn, board, x):
            return self.coord_danger_from_rook_queen(xn, board, x)
        elif self.coord_danger_from_bishop_queen(xn, board, x):
            return self.coord_danger_from_bishop_queen(xn, board, x)
        elif self.coord_danger_from_knight(xn, board, x):
            return self.coord_danger_from_knight(xn, board, x)
        elif self.coord_danger_from_pawn(xn, board, x):
            return self.coord_danger_from_pawn(xn, board, x)
        elif self.coord_danger_from_king(xn, board, x):
            return self.coord_danger_from_king(xn, board, x)

    def coord_danger_from_knight(self, xn, board, x):
        possible_coordinates = [chr(ord(xn[0]) + 1) + str(int(xn[1]) - 2), chr(ord(xn[0]) + 2) + str(int(xn[1]) - 1),
                                chr(ord(xn[0]) + 2) + str(int(xn[1]) + 1), chr(ord(xn[0]) + 1) + str(int(xn[1]) + 2),
                                chr(ord(xn[0]) - 1) + str(int(xn[1]) + 2), chr(ord(xn[0]) - 2) + str(int(xn[1]) + 1),
                                chr(ord(xn[0]) - 2) + str(int(xn[1]) - 1), chr(ord(xn[0]) - 1) + str(int(xn[1]) - 2)]
        threat_coordinates = list(set(possible_coordinates).intersection(set(self.chess_board_keys)))

        if x == 'w':
            for i in threat_coordinates:
                if board[i] == 'bf':
                    return i
        elif x == 'b':
            for i in threat_coordinates:
                if board[i] == 'wf':
                    return i

    def coord_danger_from_rook_queen(self, xn, board, x):
        threat_coordinates = []

        if int(xn[1]) != 1:  # from xn checking downwards if possible
            checked_coordinate = xn[0] + str(int(xn[1]) - 1)
            end_of_col = False
            while board[checked_coordinate] == '  ' and not end_of_col:
                if int(checked_coordinate[1]) != 1:
                    checked_coordinate = checked_coordinate[0] + str(int(checked_coordinate[1]) - 1)
                else:
                    end_of_col = True
            if board[checked_coordinate] != '  ':
                threat_coordinates.append(checked_coordinate)

        if int(xn[1]) != 8:  # from xn checking upwards if possible
            checked_coordinate = xn[0] + str(int(xn[1]) + 1)
            end_of_col = False
            while board[checked_coordinate] == '  ' and not end_of_col:
                if int(checked_coordinate[1]) != 8:
                    checked_coordinate = checked_coordinate[0] + str(int(checked_coordinate[1]) + 1)
                else:
                    end_of_col = True
            if board[checked_coordinate] != '  ':
                threat_coordinates.append(checked_coordinate)

        if xn[0] != 'h':  # from xn checking rightwards if possible
            checked_coordinate = chr(ord(xn[0]) + 1) + xn[1]
            end_of_row = False
            while board[checked_coordinate] == '  ' and not end_of_row:
                if checked_coordinate[0] != 'h':
                    checked_coordinate = chr(ord(checked_coordinate[0]) + 1) + checked_coordinate[1]
                else:
                    end_of_row = True
            if board[checked_coordinate] != '  ':
                threat_coordinates.append(checked_coordinate)

        if xn[0] != 'a':  # from xn checking leftwards if possible
            checked_coordinate = chr(ord(xn[0]) - 1) + xn[1]
            end_of_row = False
            while board[checked_coordinate] == '  ' and not end_of_row:
                if checked_coordinate[0] != 'a':
                    checked_coordinate = chr(ord(checked_coordinate[0]) - 1) + checked_coordinate[1]
                else:
                    end_of_row = True
            if board[checked_coordinate] != '  ':
                threat_coordinates.append(checked_coordinate)

        if x == 'w':
            for i in threat_coordinates:
                if board[i] == 'bT' or board[i] == 'b*':
                    return i
        elif x == 'b':
            for i in threat_coordinates:
                if board[i] == 'wT' or board[i] == 'w*':
                    return i

    def coord_danger_from_bishop_queen(self, xn, board, x):
        threat_coordinates = []

        if xn[0] != 'h' and int(xn[1]) != 1:  # from xn checking downwards right if possible
            checked_coordinate = chr(ord(xn[0]) + 1) + str(int(xn[1]) - 1)
            end_of_diagonal = False
            while board[checked_coordinate] == '  ' and not end_of_diagonal:
                if checked_coordinate[0] != 'h' and int(checked_coordinate[1]) != 1:
                    checked_coordinate = chr(ord(checked_coordinate[0]) + 1) + str(int(checked_coordinate[1]) - 1)
                else:
                    end_of_diagonal = True
            if board[checked_coordinate] != '  ':
                threat_coordinates.append(checked_coordinate)

        if xn[0] != 'h' and int(xn[1]) != 8:  # from xn checking upwards right if possible
            checked_coordinate = chr(ord(xn[0]) + 1) + str(int(xn[1]) + 1)
            end_of_diagonal = False
            while board[checked_coordinate] == '  ' and not end_of_diagonal:
                if checked_coordinate[0] != 'h' and int(checked_coordinate[1]) != 8:
                    checked_coordinate = chr(ord(checked_coordinate[0]) + 1) + str(int(checked_coordinate[1]) + 1)
                else:
                    end_of_diagonal = True
            if board[checked_coordinate] != '  ':
                threat_coordinates.append(checked_coordinate)

        if xn[0] != 'a' and int(xn[1]) != 8:  # from xn checking upwards left if possible
            checked_coordinate = chr(ord(xn[0]) - 1) + str(int(xn[1]) + 1)
            end_of_diagonal = False
            while board[checked_coordinate] == '  ' and not end_of_diagonal:
                if checked_coordinate[0] != 'a' and int(checked_coordinate[1]) != 8:
                    checked_coordinate = chr(ord(checked_coordinate[0]) - 1) + str(int(checked_coordinate[1]) + 1)
                else:
                    end_of_diagonal = True
            if board[checked_coordinate] != '  ':
                threat_coordinates.append(checked_coordinate)

        if xn[0] != 'a' and int(xn[1]) != 1:  # from xn checking downwards left if possible
            checked_coordinate = chr(ord(xn[0]) - 1) + str(int(xn[1]) - 1)
            end_of_diagonal = False
            while board[checked_coordinate] == '  ' and not end_of_diagonal:
                if checked_coordinate[0] != 'a' and int(checked_coordinate[1]) != 1:
                    checked_coordinate = chr(ord(checked_coordinate[0]) - 1) + str(int(checked_coordinate[1]) - 1)
                else:
                    end_of_diagonal = True
            if board[checked_coordinate] != '  ':
                threat_coordinates.append(checked_coordinate)

        if x == 'w':
            for i in threat_coordinates:
                if board[i] == 'bA' or board[i] == 'b*':
                    return i
        elif x == 'b':
            for i in threat_coordinates:
                if board[i] == 'wA' or board[i] == 'w*':
                    return i

    def coord_danger_from_king(self, xn, board, x):
        possible_coordinates = [chr(ord(xn[0]) - 1) + str(int(xn[1]) - 1), xn[0] + str(int(xn[1]) - 1),
                                chr(ord(xn[0]) + 1) + str(int(xn[1]) - 1), chr(ord(xn[0]) - 1) + xn[1],
                                chr(ord(xn[0]) + 1) + xn[1], chr(ord(xn[0]) - 1) + str(int(xn[1]) + 1),
                                xn[0] + str(int(xn[1]) + 1), chr(ord(xn[0]) + 1) + str(int(xn[1]) + 1)]
        threat_coordinates = list(set(possible_coordinates).intersection(set(self.chess_board_keys)))

        if x == 'w':
            for i in threat_coordinates:
                if board[i] == 'b+':
                    return i
        elif x == 'b':
            for i in threat_coordinates:
                if board[i] == 'w+':
                    return i

    def coord_danger_from_pawn(self, xn, board, x):
        possible_coordinates = []
        if x == 'w':
            possible_coordinates.append(chr(ord(xn[0]) - 1) + str(int(xn[1]) + 1))
            possible_coordinates.append(chr(ord(xn[0]) + 1) + str(int(xn[1]) + 1))
        elif x == 'b':
            possible_coordinates.append(chr(ord(xn[0]) - 1) + str(int(xn[1]) - 1))
            possible_coordinates.append(chr(ord(xn[0]) + 1) + str(int(xn[1]) - 1))
        threat_coordinates = list(set(possible_coordinates).intersection(set(self.chess_board_keys)))

        if x == 'w':
            for i in threat_coordinates:
                if board[i] == 'bi':
                    return i
        elif x == 'b':
            for i in threat_coordinates:
                if board[i] == 'wi':
                    return i

    def check_if_game_still_going(self):
        if self.currently_selected.get() != 'exit':
            if self.check_for_checkmate(self.current_player):
                self.game_still_going = False
                self.c_chess.itemconfigure('square', state=tk.DISABLED)
                self.winner = self.other_player
            elif self.check_for_stalemate(self.current_player):
                self.game_still_going = False
                self.c_chess.itemconfigure('square', state=tk.DISABLED)

    def check_for_checkmate(self, x):
        if not self.legal_move_possible(x) and self.king_in_check(x, self.chess_board):
            return True
        return False

    def check_for_stalemate(self, x):
        if not self.legal_move_possible(x):
            return True
        return False

    def legal_move_possible(self, x):
        current_player_positions = []
        for i in self.chess_board_keys:
            if self.chess_board[i][0] == x:
                current_player_positions.append(i)
        for i in current_player_positions:
            self.position1 = i
            for j in self.chess_board_keys:
                self.position2 = j
                if self.chess_board[self.position2] not in [x + 'T', x + 'f', x + 'A', x + '+', x + '*', x + 'i'] and \
                        self.check_game_rules() and not self.virtual_move_results_check(x):
                    return True
        return False

    def king_in_check(self, x, board):
        king_position = None
        for i in self.chess_board_keys:
            if board[i] == x + '+':
                king_position = i
        if self.coord_danger_from(king_position, board, x):
            return True
        return False

    def ask_for_new_game(self):
        if self.currently_selected.get() != 'exit':
            if self.winner == 'w':
                message = 'White wins the game.'
            elif self.winner == 'b':
                message = 'Black wins the game.'
            else:
                message = 'The game is a draw.'
            start_new_game = tk.messagebox.askyesno(title='End of game', message=message, detail='Start new game?')
            if not start_new_game:
                print('Exiting chess')
                self.start_new_game = False
                self.master.destroy()
            else:
                print('Setting up new game')


if __name__ == '__main__':
    root = tk.Tk()
    Chess(root)
    root.mainloop()
