import tkinter as tk
from tkinter import ttk, messagebox, filedialog


def char_range(c1, c2):     # stackoverflow.com/questions/7001144/range-over-character-in-python
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
        # widget parameters
        self.canvas_color = {'light': 'grey75', 'medium': 'grey50'}
        # square parameters
        self.square_size = int(self.screen_size[1] / 10.97)  # 70 for 1366x768
        self.square_color = {'light': '#fef0d6', 'light_hl': '#ff836b', 'dark': '#7d564a', 'dark_hl': '#be3625',
                             'l_green': '#7ff86b', 'd_green': '#3eab25'}
        # piece parameters
        self.piece_size = int(self.square_size * (5 / 7))  # 50 for 1366x768
        self.piece_color = {'light': '#d2ac79', 'light_hl': '#f4541e', 'dark': '#2a1510', 'dark_hl': '#ca2e04'}
        # font parameters (size 20 for 1366x768)
        self.font = {'size': int(self.square_size / 3.5), 'color': 'black', 'type': 'TKDefaultFont'}

        self.chess_board = {}                           # game save values start
        self.captured_pieces = {}
        self.current_player = None
        self.current_player2 = None
        self.other_player = None
        self.these_rook_king_moved = []
        self.en_pass_pos = None
        self.number_of_player = tk.IntVar(value=2)      # game save values end
        self.chess_board_keys = None
        self.c_chess = None
        self.currently_selected = tk.StringVar()
        self.show_legal_moves = tk.BooleanVar(value=True)
        self.file_to_load = 'initial_setup.txt'
        self.c = {}      # dictionary for gui elements created later and used for multiple methods
        self.bak = {}    # dictionary for backups
        self.position1 = None
        self.position2 = None
        self.selected_piece = None
        self.game_still_going = True
        self.winner = None
        self.castling_rook = None  # tempo info holder for castling
        self.king_position = None  # tempo info holder for castling
        self.game_is_saved = False

        self.start_new_game = True
        while self.start_new_game:
            self.play_game()

    def play_game(self):
        self.clear_previous_session()
        self.load_board_setup()
        self.display_board()  # legacy display in terminal
        self.draw_menu()
        self.draw_4_main_canvas()
        self.draw_chess_board()
        self.draw_captured_areas()
        self.draw_captured_pieces()
        self.draw_squares()
        self.draw_pieces()
        while self.game_still_going:
            if (self.number_of_player.get() == 1 and self.current_player2 == 'man') or self.number_of_player.get() == 2:
                self.handle_turn(self.current_player)
                if self.promotion_coordinate(self.current_player):
                    self.promotion_dialog(self.current_player)
            elif self.number_of_player.get() == 1 and self.current_player2 == 'computer':
                print('computer turn')    # todo computer
            self.game_is_saved = False
            self.flip_player()
            self.check_if_game_still_going(self.current_player)
        self.ask_for_new_game()

    def clear_previous_session(self):
        self.game_still_going = True
        self.winner = None
        for widget in self.master.winfo_children():
            print('destroying' + str(widget))
            widget.destroy()

    def load_board_setup(self):
        try:
            file = open(self.file_to_load, 'r')
            data = file.read().splitlines()
            self.chess_board = {line.split('=')[0]: line.split('=')[1] for line in data[0:64]}
            self.captured_pieces['w'] = [line.split('=')[1] for line in data[65:81]]
            self.captured_pieces['b'] = [line.split('=')[1] for line in data[81:97]]
            self.current_player = data[97].split('=')[1]
            self.current_player2 = data[98].split('=')[1]
            self.other_player = data[99].split('=')[1]
            rook_king_moved_string = data[100].split('=')[1]
            self.these_rook_king_moved = rook_king_moved_string.split(',')
            en_pass_pos_string = data[101].split('=')[1]
            self.en_pass_pos = en_pass_pos_string.split(',')
            self.number_of_player.set(data[102].split('=')[1])
            file.close()
            self.chess_board_keys = list(self.chess_board.keys())
        except FileNotFoundError as error:
            print(error)
            tk.messagebox.showerror(title='Error', message='initial_setup.txt is missing from game directory!')
            self.master.destroy()
        except IndexError:
            print('Game file is corrupted!')
            tk.messagebox.showerror(title='Error', message='Game file is corrupted!')
            self.chess_board = self.bak['chess_board'].copy()    # restoring backups
            self.captured_pieces = self.bak['captured_pieces'].copy()
            self.current_player = self.bak['current_player']
            self.current_player2 = self.bak['current_player2']
            self.other_player = self.bak['other_player']
            self.these_rook_king_moved = self.bak['these_rook_king_moved'].copy()
            self.en_pass_pos = self.bak['en_pass_pos'].copy()
            self.number_of_player = self.bak['number_of_player']

    def display_board(self):
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

    def draw_menu(self):
        self.master.option_add('*tearOff', False)
        main_menu = tk.Menu(self.master)
        self.master['menu'] = main_menu
        file_menu = tk.Menu(main_menu)
        options_menu = tk.Menu(main_menu)
        main_menu.add_cascade(label='File', menu=file_menu, underline=0)
        main_menu.add_cascade(label='Options', menu=options_menu, underline=0)
        file_menu.add_command(label='New Game', command=self.new_game)
        file_menu.add_command(label='Load Game', command=self.load_game)
        file_menu.add_command(label='Save Game', command=self.save_game)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.exit_game)
        options_menu.add_command(label='Board size')
        options_menu.add_command(label='Settings', command=self.settings_dialog)

        self.c['castling_menu'] = tk.Menu(self.master)   # context menu
        self.c['castling_menu'].add_command(label='Castling', command=self.castling)

        self.master.protocol("WM_DELETE_WINDOW", lambda: self.exit_game())  # intercepting close button

    def new_game(self):
        new_response = tk.messagebox.askyesno(title='New game', message='Do you want to start new game?')
        if new_response:
            self.game_still_going = False
            self.file_to_load = 'initial_setup.txt'
            self.currently_selected.set('exit')
            print('Setting up new game')

    def load_game(self):
        path = tk.filedialog.askopenfilename(filetypes=[('Text Documents', '*.txt')])
        if path:
            self.bak['chess_board'] = self.chess_board.copy()  # saving backups
            self.bak['captured_pieces'] = self.captured_pieces.copy()
            self.bak['current_player'] = self.current_player
            self.bak['current_player2'] = self.current_player2
            self.bak['other_player'] = self.other_player
            self.bak['these_rook_king_moved'] = self.these_rook_king_moved.copy()
            self.bak['en_pass_pos'] = self.en_pass_pos.copy()
            self.bak['number_of_player'] = self.number_of_player
            self.game_still_going = False
            self.file_to_load = path
            self.currently_selected.set('exit')
            print('Loading game from file')

    def save_game(self):
        path = tk.filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text Documents', '*.txt')])
        if path:
            file = open(path, 'w')
            for key in self.chess_board:
                file.write(key + '=' + self.chess_board[key] + '\n')
            file.write('captured pieces\n')
            captured_indexes = {}
            for color in ['w', 'b']:
                captured_indexes[color] = [color + str(i) for i in range(16)]
                for pos, value in list(zip(captured_indexes[color], self.captured_pieces[color])):
                    file.write(pos + '=' + value + '\n')
            file.write('current_player=' + self.current_player + '\n')
            file.write('current_player2=' + self.current_player2 + '\n')
            file.write('other_player=' + self.other_player + '\n')
            file.write('these_rook_king_moved=' + ','.join(self.these_rook_king_moved) + '\n')
            file.write('en_pass_pos=' + ','.join(self.en_pass_pos) + '\n')
            file.write('number_of_player=' + str(self.number_of_player.get()))
            file.close()
            self.game_is_saved = True
            print('Game is saved')
            return True

    def exit_game(self):
        def exiting():
            self.start_new_game = False
            self.game_still_going = False
            self.currently_selected.set('exit')
            print('Exiting chess')
            self.master.destroy()

        if self.game_is_saved:
            exit_response = tk.messagebox.askyesno(title='Quit game', message='Do you want to exit game?')
            if exit_response:
                exiting()
        else:
            save_response = tk.messagebox.askyesno(title='Save game', message='Do you want to save before exit?')
            if save_response:
                if self.save_game():    # user didn't click on cancel, otherwise no exit
                    exiting()
            else:
                exiting()

    def settings_dialog(self):
        show_legal_moves2 = tk.BooleanVar(value=self.show_legal_moves.get())
        number_of_player2 = tk.IntVar(value=self.number_of_player.get())
        settings_selected = tk.BooleanVar()

        settings_window = tk.Toplevel(self.master)
        settings_window.title('Settings')
        settings_window.resizable(False, False)
        settings_window.protocol("WM_DELETE_WINDOW", lambda: settings_selected.set(True))

        settings_frame = ttk.Frame(settings_window, padding=10)
        settings_frame.grid(column=0, row=0, sticky='n, w, e, s')

        message1 = ttk.Label(settings_frame, text='Single player mode with computer:', padding=5)
        message2 = ttk.Label(settings_frame, text='Highlight legal movement squares with green:', padding=5)
        message1.grid(column=0, row=0, columnspan=3, sticky='n, w')
        message2.grid(column=0, row=1, columnspan=3, sticky='n, w')
        player_number_button = \
            ttk.Checkbutton(settings_frame, variable=number_of_player2, onvalue=1, offvalue=2, padding=5)
        legal_moves_button = \
            ttk.Checkbutton(settings_frame, variable=show_legal_moves2, onvalue=True, offvalue=False, padding=5)
        player_number_button.grid(column=3, row=0, sticky='n, e')
        legal_moves_button.grid(column=3, row=1, sticky='n, e')

        def apply_button_logic():
            self.show_legal_moves.set(show_legal_moves2.get())
            self.number_of_player.set(number_of_player2.get())
            settings_selected.set(True)
        apply_button = ttk.Button(settings_frame, text='Apply', command=apply_button_logic)
        cancel_button = ttk.Button(settings_frame, text='Cancel', command=lambda: settings_selected.set(True))
        apply_button.grid(column=2, row=2, sticky='n, e, s')
        cancel_button.grid(column=3, row=2, sticky='n, s')

        root.wait_variable(settings_selected)
        settings_window.destroy()

    def draw_4_main_canvas(self):
        self.c['left_side'] = self.screen_size[1] - 100  # 92 plus 3 + 5
        self.c['right_width'] = self.screen_size[0] - self.c['left_side'] - 24  # 2blue edge,12separator, 5,5 pad x
        c_right_center_height = self.c['left_side'] / 4
        self.c['right_top_height'] = (self.c['left_side'] - c_right_center_height - 24) / 2  # 12 x 2 separator

        self.c['left'] = tk.Canvas(self.master, width=self.c['left_side'], height=self.c['left_side'])
        self.c['right_top'] = tk.Canvas(self.master, width=self.c['right_width'], height=self.c['right_top_height'])
        self.c['right_bottom'] = tk.Canvas(self.master, width=self.c['right_width'], height=self.c['right_top_height'])
        self.c['right_center'] = tk.Canvas(self.master, width=self.c['right_width'], height=c_right_center_height)
        for canvas_item in [self.c['left'], self.c['right_top'], self.c['right_bottom'], self.c['right_center']]:
            canvas_item['bg'] = self.canvas_color['light']
            canvas_item['highlightthickness'] = 0
        separator1 = ttk.Separator(self.master, orient='vertical')
        separator2 = ttk.Separator(self.master, orient='horizontal')
        separator3 = ttk.Separator(self.master, orient='horizontal')

        self.c['left'].grid(column=0, row=0, columnspan=1, rowspan=5, padx=5, pady=(3, 0))
        separator1.grid(column=1, row=0, columnspan=1, rowspan=5, sticky='n, s')
        self.c['right_top'].grid(column=2, row=0, padx=(5, 0), pady=(3, 5))
        separator2.grid(column=2, row=1, sticky='w, e')
        self.c['right_center'].grid(column=2, row=2, padx=(5, 0), pady=5)
        separator3.grid(column=2, row=3, sticky='w, e')
        self.c['right_bottom'].grid(column=2, row=4, padx=(5, 0), pady=(5, 0))

        self.c['current_player_label'] = self.c['right_center'].create_text(
            self.c['right_width'] / 2, c_right_center_height / 2,
            text='White is next to move', fill=self.font['color'],
            font=(self.font['type'], self.font['size']))

        self.master.bind('<Button-3>', lambda e: self.reset_selection())
        self.master.bind('<Escape>', lambda e: self.reset_selection())

    def draw_chess_board(self):
        notation_strip_width = (self.c['left_side'] - self.square_size * 8) / 2

        self.c_chess = tk.Canvas(self.c['left'], width=self.square_size * 8, height=self.square_size * 8,
                                 bg=self.canvas_color['light'])

        for i in ['abc_n', 'abc_s']:  # creating two rows of letters a-h
            self.c[i] = tk.Canvas(self.c['left'], width=self.square_size * 8,
                                  height=notation_strip_width, bg=self.canvas_color['medium'])
            for j in char_range('a', 'h'):
                self.c[i].create_text(
                    self.square_size * (ord(j) - 96.5), notation_strip_width / 2,
                    text=j, fill=self.font['color'], font=(self.font['type'], self.font['size']))

        for i in ['123_w', '123_e']:  # creating two columns of numbers 1-8
            self.c[i] = tk.Canvas(self.c['left'], width=notation_strip_width,
                                  height=self.c['left_side'], bg=self.canvas_color['medium'])
            for j in range(0, 8):
                self.c[i].create_text(
                    notation_strip_width / 2, self.c['left_side'] - notation_strip_width - self.square_size * (j + 0.5),
                    text=j + 1, fill=self.font['color'], font=(self.font['type'], self.font['size']))

        for canvas_item in [self.c_chess, self.c['abc_n'], self.c['abc_s'], self.c['123_w'], self.c['123_e']]:
            canvas_item['highlightthickness'] = 0

        self.c['123_w'].grid(column=0, row=0, rowspan=3)
        self.c['abc_n'].grid(column=1, row=0)
        self.c_chess.grid(column=1, row=1)
        self.c['abc_s'].grid(column=1, row=2)
        self.c['123_e'].grid(column=2, row=0, rowspan=3)

    def draw_captured_areas(self):
        self.c['captured'] = {}  # creating two areas for captured pieces
        for color, parent, y in [('w', self.c['right_bottom'], self.c['right_top_height'] - self.square_size * 3),
                                 ('b', self.c['right_top'], self.square_size)]:
            self.c['captured'][color] = tk.Canvas(parent, width=self.square_size * 8,
                                                  height=self.square_size * 2, bg=self.canvas_color['medium'],
                                                  highlightthickness=0)
            self.c['captured'][color].place(anchor='n', x=self.c['right_width'] / 2, y=y)

        self.c['right_top'].create_text(self.c['right_width'] / 2, self.square_size / 2,
                                        text='Captured black pieces', fill=self.font['color'],
                                        font=(self.font['type'], self.font['size']))

        self.c['right_bottom'].create_text(self.c['right_width'] / 2, self.c['right_top_height'] - self.square_size / 2,
                                           text='Captured white pieces', fill=self.font['color'],
                                           font=(self.font['type'], self.font['size']))

    def draw_captured_pieces(self):
        def get_captured_center(number):
            if number < 8:
                x = (number + 0.5) * self.square_size
                y = self.square_size * 0.5
            else:
                x = (number - 7.5) * self.square_size
                y = self.square_size * 1.5
            return x, y

        for color in ['b', 'w']:
            for i in range(0, 16):
                self.c['captured'][color].create_text(
                    get_captured_center(i),
                    text=self.txt_map_piece(self.captured_pieces[color][i][1]),
                    tag=f'captured_{str(i)}',
                    fill=self.txt_map_color(color)[0],
                    activefill=self.txt_map_color(color)[1],  # not used yet
                    font=(self.font['type'], self.piece_size),
                    state=tk.DISABLED)
        # for i in range(1, 17):
        #     print(self.c['captured']['w'].gettags(i))

    def pos_map_color(self, pos):
        if (ord(pos[0]) + int(pos[1])) % 2 == 0:  # True if dark square, False if light square
            color = self.square_color['dark']
            act_color = self.square_color['dark_hl']
            green_color = self.square_color['d_green']
        else:
            color = self.square_color['light']
            act_color = self.square_color['light_hl']
            green_color = self.square_color['l_green']
        return color, act_color, green_color

    def draw_squares(self):
        for i in self.chess_board_keys:
            x0 = (ord(i[0]) - 97) * self.square_size
            y0 = abs(int(i[1]) - 8) * self.square_size
            x1 = (ord(i[0]) - 96) * self.square_size
            y1 = abs(int(i[1]) - 9) * self.square_size
            self.c_chess.create_rectangle(x0, y0, x1, y1, fill=self.pos_map_color(i)[0], width=0,
                                          activefill=self.pos_map_color(i)[1], tag=('square', 'square_' + i))
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
            return self.piece_color['light'], self.piece_color['light_hl']
        elif color == 'b':
            return self.piece_color['dark'], self.piece_color['dark_hl']

    def draw_pieces(self):
        def drawing(pos, color):
            if self.chess_board[pos][1] == 'T':
                tag = ('piece', color, 'piece_' + pos, 'T')
            else:
                tag = ('piece', color, 'piece_' + pos)
            self.c_chess.create_text(
                self.get_square_center(pos),
                text=self.txt_map_piece(self.chess_board[pos][1]),
                tag=tag,
                fill=self.txt_map_color(color)[0],
                activefill=self.txt_map_color(color)[1],
                font=(self.font['type'], self.piece_size))

        for i in self.chess_board_keys:
            if self.chess_board[i] != '  ':
                if self.chess_board[i][0] == 'w':
                    drawing(i, 'w')
                elif self.chess_board[i][0] == 'b':
                    drawing(i, 'b')
            # all tags has to be bound, otherwise not able to move piece after initial move
            self.c_chess.tag_bind('piece_' + i, '<Button-1>', lambda e, n=i: self.currently_selected.set(n))
            # Button-3 for Castling context menu
            self.c_chess.tag_bind('piece_' + i, '<Button-3>', lambda e, n=i: self.castling_context(e, n))

    def castling_context(self, e, n):
        # castling 1. check: only Rooks respond to right click
        if 'T' in self.c_chess.gettags(self.c_chess.find_withtag(f'piece_{n}')):
            print('castling requested with: rook_' + str(n))
            self.king_position = None
            for i in self.chess_board_keys:
                if self.chess_board[i] == self.current_player + '+':
                    self.king_position = i
            print("current player king position: " + self.king_position)
            print('These (rook and) king moved so far: ' + str(self.these_rook_king_moved))
            print('This rook moved: ', end='')
            print(n in self.these_rook_king_moved)
            print('This king moved: ', end='')
            print(self.king_position in self.these_rook_king_moved)
            self.castling_rook = n
            # castling 2. check: menu appears only if selected Rook and current player King hasn't moved so far
            if self.king_position not in self.these_rook_king_moved and n not in self.these_rook_king_moved:
                self.c['castling_menu'].post(e.x_root, e.y_root)

    def castling(self):
        def empty_space_between_king_rook():
            if self.castling_rook[0] == 'h':
                if self.chess_board['g' + self.castling_rook[1]] == '  ' and \
                        self.chess_board['f' + self.castling_rook[1]] == '  ':
                    return True
            elif self.castling_rook[0] == 'a':
                if self.chess_board['b' + self.castling_rook[1]] == '  ' and \
                        self.chess_board['c' + self.castling_rook[1]] == '  ' and \
                        self.chess_board['d' + self.castling_rook[1]] == '  ':
                    return True
            return False

        def king_castling_safe():
            if self.castling_rook[0] == 'h':
                if self.coord_danger_from(self.king_position, self.chess_board, self.current_player) or\
                        self.coord_danger_from('f' + self.king_position[1], self.chess_board, self.current_player) or \
                        self.coord_danger_from('g' + self.king_position[1], self.chess_board, self.current_player):
                    return False
            elif self.castling_rook[0] == 'a':
                if self.coord_danger_from(self.king_position, self.chess_board, self.current_player) or\
                        self.coord_danger_from('d' + self.king_position[1], self.chess_board, self.current_player) or \
                        self.coord_danger_from('c' + self.king_position[1], self.chess_board, self.current_player):
                    return False
            return True

        def modify_rook_king(color):
            rook_id = self.c_chess.find_withtag(f'piece_{self.castling_rook}')
            self.c_chess.itemconfigure(rook_id, fill=self.txt_map_color(self.current_player)[color])
            king_id = self.c_chess.find_withtag(f'piece_{self.king_position}')
            self.c_chess.itemconfigure(king_id, fill=self.txt_map_color(self.current_player)[color])
            return rook_id, king_id     # also extracts object id

        def get_row_col(color, k_col):
            if color == 'w':
                row = str(1)
            else:
                row = str(8)
            if k_col == 'g':
                r_col = 'f'
            else:
                r_col = 'd'
            return row, r_col

        def backend_castling(color, k_col):
            self.chess_board[k_col + get_row_col(color, k_col)[0]] = color + '+'
            self.chess_board[self.king_position] = '  '
            self.chess_board[get_row_col(color, k_col)[1] + get_row_col(color, k_col)[0]] = color + 'T'
            self.chess_board[self.castling_rook] = '  '
            self.these_rook_king_moved.append(k_col + self.king_position[1])

        def gui_castling(color, k_col):     # moving and updating tag
            self.c_chess.coords(modify_rook_king(0)[0],     # setting color back together with return id
                                self.get_square_center(get_row_col(color, k_col)[1] + get_row_col(color, k_col)[0]))
            self.c_chess.coords(modify_rook_king(0)[1],  # setting color back together with return id
                                self.get_square_center(k_col + get_row_col(color, k_col)[0]))
            self.c_chess.itemconfigure(self.c_chess.find_withtag(f'piece_{self.castling_rook}'),
                                       tag=('piece', color,
                                            'piece_' + get_row_col(color, k_col)[1] + get_row_col(color, k_col)[0],
                                       'T'))  # update tag of piece
            self.c_chess.itemconfigure(self.c_chess.find_withtag(f'piece_{self.king_position}'),
                                       tag=('piece', color,
                                            'piece_' + k_col + get_row_col(color, k_col)[0]))

        # castling 3. check: castling dialog only appears if squares empty between king and chosen rook
        if not empty_space_between_king_rook():
            tk.messagebox.showwarning(title='Castling', message='Piece present between king and chosen rook!')
        else:
            modify_rook_king(1)
            if self.castling_rook[0] == 'h':
                message = 'Proceed with kingside castling?'
                side = 'g'
            else:
                message = 'Proceed with queenside castling?'
                side = 'c'
            do_castling = tk.messagebox.askyesno(title='Castling', message=message)
            if do_castling:
                # castling 4. check: castling happens only if king not in check during castling
                if not king_castling_safe():
                    tk.messagebox.showwarning(title='Illegal move', message='King in check during castling!')
                    modify_rook_king(0)
                else:
                    print('castling with: rook_' + self.castling_rook)
                    backend_castling(self.current_player, side)
                    gui_castling(self.current_player, side)
                    self.currently_selected.set('exit')     # to bypass anticipated position1 and flip player
                    self.display_board()
            else:
                modify_rook_king(0)

    def en_passant(self, x):
        if self.chess_board[self.position1][1] == 'i' and self.position2 == self.en_pass_pos[0]:
            first_empty_slot = self.captured_pieces[self.other_player].index('  ')
            self.captured_pieces[self.other_player][first_empty_slot] = self.chess_board[self.en_pass_pos[1]]
            # copy captured piece to captured canvas
            self.c['captured'][self.other_player].itemconfigure(
                self.c['captured'][self.other_player].find_withtag('captured_' + str(first_empty_slot)),
                text=self.txt_map_piece(self.chess_board[self.en_pass_pos[1]][1]))
            # get id of captured piece
            captured_piece = self.c_chess.find_withtag(f'piece_{self.en_pass_pos[1]}')
            print('En passant! captured id=' + str(captured_piece))
            # delete captured piece from chess board
            self.c_chess.delete(captured_piece)
            self.chess_board[self.en_pass_pos[1]] = '  '
        if x == 'w':
            if self.chess_board[self.position1][1] == 'i' and self.position2[1] == '4':
                self.en_pass_pos[0] = self.position2[0] + str(3)
                self.en_pass_pos[1] = self.position2
            else:
                self.en_pass_pos = ['  ', '  ']
        elif x == 'b':
            if self.chess_board[self.position1][1] == 'i' and self.position2[1] == '5':
                self.en_pass_pos[0] = self.position2[0] + str(6)
                self.en_pass_pos[1] = self.position2
            else:
                self.en_pass_pos = ['  ', '  ']
        if self.en_pass_pos != ['  ', '  ']:
            print(f'En passant possible for {self.en_pass_pos[1]}, capture at {self.en_pass_pos[0]}')

    def handle_turn(self, x):
        self.selected_piece = None
        # for i in range(1, 97):
        #     print(i, end=' ')
        #     print(self.c_chess.gettags(i))
        if x == 'w':
            print('White is next to move')
            self.c['right_center'].itemconfigure(self.c['current_player_label'], text='White is next to move')
        elif x == 'b':
            print('Black is next to move')
            self.c['right_center'].itemconfigure(self.c['current_player_label'], text='Black is next to move')

        self.c_chess.itemconfigure('piece', state=tk.DISABLED)  # initialize select piece
        self.c_chess.itemconfigure('square', state=tk.DISABLED)
        self.c_chess.itemconfigure(x, state=tk.NORMAL)
        print('waiting for position1')
        self.c_chess.wait_variable(self.currently_selected)
        if self.currently_selected.get() != 'exit':  # if user didn't close program meanwhile
            self.position1 = self.currently_selected.get()
            print('position1=' + self.position1)
            self.selected_piece = self.c_chess.find_withtag(f'piece_{self.position1}')  # get id of selected piece
            print('id=' + str(self.selected_piece[0]))
            self.c_chess.itemconfigure(self.selected_piece, fill=self.txt_map_color(x)[1])  # set constant red

            self.c_chess.itemconfigure('piece', state=tk.DISABLED)  # initialize select square
            valid_position2s = self.generate_valid_position2(x)     # activate only valid movement squares
            if self.show_legal_moves.get():
                color_number = 2
            else:
                color_number = 0
            for i in valid_position2s:
                self.c_chess.itemconfigure('square_' + i, state=tk.NORMAL, fill=self.pos_map_color(i)[color_number])

            print('waiting for position2')
            # in this timeframe there's possibility to reset selection
            self.c_chess.wait_variable(self.currently_selected)

            if self.selected_piece is not None and self.currently_selected.get() != 'exit':
                self.position2 = self.currently_selected.get()
                print('position2=' + self.position2)

                if not self.virtual_move_results_check(x):
                    self.en_passant(self.current_player)
                    # if capture happens
                    if self.chess_board[self.position2] != '  ':
                        first_empty_slot = self.captured_pieces[self.other_player].index('  ')
                        # backend, copying position2 piece to other player's captured list
                        self.captured_pieces[self.other_player][first_empty_slot] = self.chess_board[self.position2]
                        # copy captured piece to captured canvas
                        self.c['captured'][self.other_player].itemconfigure(
                            self.c['captured'][self.other_player].find_withtag('captured_' + str(first_empty_slot)),
                            text=self.txt_map_piece(self.chess_board[self.position2][1]))
                        # get id of captured piece
                        captured_piece = self.c_chess.find_withtag(f'piece_{self.position2}')
                        print('Capture! captured id=' + str(captured_piece))
                        # delete captured piece from chess board
                        self.c_chess.delete(captured_piece)

                    # register first move of rook and king for castling
                    if self.chess_board[self.position1][1] == '+' or self.chess_board[self.position1][1] == 'T':
                        self.these_rook_king_moved.append(self.position2)
                        if self.position1 in self.these_rook_king_moved:
                            self.these_rook_king_moved.remove(self.position1)

                    # backend, moving piece in the chess dictionary
                    self.chess_board[self.position2] = self.chess_board[self.position1]
                    self.chess_board[self.position1] = '  '
                    self.c_chess.coords(self.selected_piece, self.get_square_center(self.position2))  # moving piece
                    self.c_chess.itemconfigure(self.selected_piece, fill=self.txt_map_color(x)[0])  # set original color
                    print('old tags=' + str(self.c_chess.gettags(self.selected_piece)))
                    self.c_chess.dtag(self.selected_piece, f'piece_{self.position1}')   # update tag of piece
                    self.c_chess.addtag(f'piece_{self.position2}', 'withtag', self.selected_piece)
                    print('new tags=' + str(self.c_chess.gettags(self.selected_piece)))
                    for i in valid_position2s:  # set squares to original color
                        self.c_chess.itemconfigure('square_' + i, fill=self.pos_map_color(i)[0])
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
            for i in self.generate_valid_position2(self.current_player):
                self.c_chess.itemconfigure('square_' + i, fill=self.pos_map_color(i)[0])
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
            if self.current_player2 == 'man':
                self.current_player2 = 'computer'
            elif self.current_player2 == 'computer':  # comment out these lines to make computer play only
                self.current_player2 = 'man'  # comment out these lines to make computer play only
        else:
            print('reset or check condition, not flipping player')

    def generate_valid_position2(self, x):
        valid_position2 = []
        for k in self.chess_board_keys:
            self.position2 = k
            if self.check_legal_move() and \
                    self.chess_board[self.position2] not in [x + 'T', x + 'f', x + 'A', x + '+', x + '*', x + 'i']:
                valid_position2.append(k)
        return valid_position2

    def promotion_coordinate(self, x):
        if x == 'w':
            for i in self.chess_board_keys[0: 8]:  # a8-h8
                if self.chess_board[i] == 'wi':
                    return i
        elif x == 'b':
            for i in self.chess_board_keys[56: 65]:  # a1-h1
                if self.chess_board[i] == 'bi':
                    return i

    def promotion_dialog(self, x):
        button_value = tk.StringVar(value='*')
        promotion_selected = tk.BooleanVar()

        promotion_window = tk.Toplevel(self.master)
        promotion_window.title('Promotion')
        promotion_window.resizable(False, False)
        promotion_window.protocol("WM_DELETE_WINDOW", lambda: promotion_selected.set(True))

        promotion_frame = ttk.Frame(promotion_window, padding=10)
        promotion_frame.grid(column=0, row=0, sticky='n, w, e, s')

        message = ttk.Label(promotion_frame,
                            text="One of your pawn reached 8th rank.\nChoose a replacement piece from the list:")
        message.grid(column=0, row=0, columnspan=4, sticky='n, w, s')

        buttons = {}  # creating radio buttons to select pieces
        for piece, label in [('*', 'Queen (♛)'), ('T', 'Rook (♜)'), ('A', 'Bishop (♝)'), ('f', 'Knight (♞)')]:
            buttons[piece] = ttk.Radiobutton(promotion_frame, text=label, variable=button_value, value=piece,
                                             padding=10)
        for piece, col in [('*', 0), ('T', 1), ('A', 2), ('f', 3)]:
            buttons[piece].grid(column=col, row=1, sticky='n, w, e, s')

        ok_button = ttk.Button(promotion_frame, text='Select', command=lambda: promotion_selected.set(True))
        ok_button.grid(column=3, row=2, sticky='n, w, e, s')

        root.wait_variable(promotion_selected)
        promotion_window.destroy()

        self.chess_board[self.promotion_coordinate(x)] = x + button_value.get()  # set backend
        self.c_chess.itemconfigure(self.selected_piece, text=self.txt_map_piece(button_value.get()))  # set frontend
        self.display_board()

    def check_legal_move(self):
        if self.chess_board[self.position1][1] == 'T':    # Rook
            if self.check_movement_cols_rows() and self.check_obstacle_cols_rows():
                return True
        if self.chess_board[self.position1][1] == 'A':    # Bishop
            if self.check_movement_diagonals() and self.check_obstacle_diagonals():
                return True
        if self.chess_board[self.position1][1] == '*':    # Queen
            if (self.check_movement_cols_rows() or self.check_movement_diagonals()) \
                    and (self.check_obstacle_cols_rows() or self.check_obstacle_diagonals()):
                return True
        if self.chess_board[self.position1][1] == '+':    # King
            if abs(ord(self.position2[0]) - ord(self.position1[0])) < 2 and \
                    abs(int(self.position2[1]) - int(self.position1[1])) < 2:
                return True
        if self.chess_board[self.position1][1] == 'f':    # Knight
            if (abs(ord(self.position2[0]) - ord(self.position1[0])) == 1 and
                abs(int(self.position2[1]) - int(self.position1[1])) == 2) or \
                    (abs(ord(self.position2[0]) - ord(self.position1[0])) == 2 and
                     abs(int(self.position2[1]) - int(self.position1[1])) == 1):
                return True
        if self.chess_board[self.position1] == 'wi':      # Pawn white
            if self.move_one_capture_side_one(-1) or self.first_move_two(2, 3, -2):
                return True
        if self.chess_board[self.position1] == 'bi':      # Pawn black
            if self.move_one_capture_side_one(1) or self.first_move_two(7, 6, 2):
                return True
        return False

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

    def move_one_capture_side_one(self, dct1):      # direction up if -1, down if 1
        if self.chess_board[self.position2] == '  ':
            if self.position2 == self.en_pass_pos[0] and \
                    abs(ord(self.position2[0]) - ord(self.position1[0])) == 1 and \
                    int(self.position1[1]) - int(self.position2[1]) == dct1:
                return True
            elif self.position1[0] == self.position2[0] and int(self.position1[1]) - int(self.position2[1]) == dct1:
                return True
            return False
        elif self.chess_board[self.position2] != '  ':
            if abs(ord(self.position2[0]) - ord(self.position1[0])) == 1 and \
                    int(self.position1[1]) - int(self.position2[1]) == dct1:
                return True
            return False

    def first_move_two(self, init_row, m_row, dct2):     # for white: init_row=2, next_row=3, direction=-2
        if int(self.position1[1]) == init_row and self.chess_board[self.position2] == '  ' and \
                self.chess_board[self.position2[0] + str(m_row)] == '  ' and \
                self.position1[0] == self.position2[0] and int(self.position1[1]) - int(self.position2[1]) == dct2:
            return True
        return False

    def virtual_move_results_check(self, x):
        chess_board_virtual = self.chess_board.copy()  # shallow copy
        chess_board_virtual[self.position2] = chess_board_virtual[self.position1]
        chess_board_virtual[self.position1] = '  '
        return self.king_in_check(x, chess_board_virtual)

    # checks if xn coordinate of x player on board is under attack from enemy and returns enemy's coordinates
    def coord_danger_from(self, xn, board, x):
        queen_rook = self.coord_danger_from_queen_rook_bishop(
            xn, board, x, [('z', 1, 0, -1), ('z', 8, 0, 1), ('h', 9, 1, 0), ('a', 9, -1, 0)], ('T', '*'))
        # check_param order: from xn checking down, up, right, left
        queen_bishop = self.coord_danger_from_queen_rook_bishop(
            xn, board, x, [('h', 1, 1, -1), ('h', 8, 1, 1), ('a', 8, -1, 1), ('a', 1, -1, -1)], ('A', '*'))
        # check_param order: from xn checking right down, right up, left up, left down
        king = self.coord_danger_from_king_knight(xn, board, x, [(-1, -1), (0, -1), (1, -1), (-1, 0),
                                                                 (1, 0), (-1, 1), (0, 1), (1, 1)], '+')
        knight = self.coord_danger_from_king_knight(xn, board, x, [(1, -2), (2, -1), (2, 1), (1, 2),
                                                                   (-1, 2), (-2, 1), (-2, -1), (-1, -2)], 'f')
        white_pawn = self.coord_danger_from_pawn(xn, board, [(-1, -1), (1, -1)], 'w')
        black_pawn = self.coord_danger_from_pawn(xn, board, [(-1, 1), (1, 1)], 'b')
        if queen_rook:
            return queen_rook
        elif queen_bishop:
            return queen_bishop
        elif king:
            return king
        elif knight:
            return knight
        elif white_pawn and x == 'b':
            return white_pawn
        elif black_pawn and x == 'w':
            return black_pawn

    def coord_danger_from_queen_rook_bishop(self, xn, board, x, check_param, pieces):

        def hor_vrt_dia_check(limit_col, limit_row, dct_c, dct_r):  # universal horizontal, vertical, diagonal
            if xn[0] != limit_col and int(xn[1]) != limit_row:
                checked_coordinate = chr(ord(xn[0]) + dct_c) + str(int(xn[1]) + dct_r)
                reached_edge = False
                while board[checked_coordinate] == '  ' and not reached_edge:
                    if checked_coordinate[0] != limit_col and int(checked_coordinate[1]) != limit_row:
                        checked_coordinate = chr(ord(checked_coordinate[0]) + dct_c) + \
                                             str(int(checked_coordinate[1]) + dct_r)
                    else:
                        reached_edge = True
                if board[checked_coordinate] != '  ':
                    threat_coordinates.append(checked_coordinate)

        threat_coordinates = []
        for k in range(len(check_param)):
            hor_vrt_dia_check(*check_param[k])
        if x == 'w':
            for i in threat_coordinates:
                if board[i] == 'b' + pieces[0] or board[i] == 'b' + pieces[1]:
                    return i
        elif x == 'b':
            for i in threat_coordinates:
                if board[i] == 'w' + pieces[0] or board[i] == 'w' + pieces[1]:
                    return i

    def coord_danger_from_king_knight(self, xn, board, x, xy, piece):
        possible_coordinates = []
        for a, b in xy:
            possible_coordinates.append(chr(ord(xn[0]) + a) + str(int(xn[1]) + b))
        threat_coordinates = list(set(possible_coordinates).intersection(set(self.chess_board_keys)))
        if x == 'w':
            for i in threat_coordinates:
                if board[i] == 'b' + piece:
                    return i
        elif x == 'b':
            for i in threat_coordinates:
                if board[i] == 'w' + piece:
                    return i

    def coord_danger_from_pawn(self, xn, board, xy, color):
        possible_coordinates = []
        for a, b in xy:
            possible_coordinates.append(chr(ord(xn[0]) + a) + str(int(xn[1]) + b))
        threat_coordinates = list(set(possible_coordinates).intersection(set(self.chess_board_keys)))
        for i in threat_coordinates:
            if board[i] == color + 'i':
                return i

    def check_if_game_still_going(self, x):
        if self.currently_selected.get() != 'exit':
            legal_move = self.legal_move_possible(x)    # to prevent running the method twice
            all_player_pos = {self.chess_board[i]: i for i in self.chess_board_keys if self.chess_board[i] != '  '}
            if not legal_move and self.king_in_check(x, self.chess_board):  # checkmate
                self.game_still_going = False
                self.c_chess.itemconfigure('square', state=tk.DISABLED)
                self.winner = self.other_player
            elif not legal_move:                                            # stalemate
                self.game_still_going = False
                self.c_chess.itemconfigure('square', state=tk.DISABLED)
            # other stalemates:
            elif {'w+', 'b+'} == set(all_player_pos):
                self.game_still_going = False       # only king - king left
                self.c_chess.itemconfigure('square', state=tk.DISABLED)
            elif {'w+', 'b+', 'wA'} == set(all_player_pos) or {'w+', 'b+', 'bA'} == set(all_player_pos):
                self.game_still_going = False       # only king - king+bishop left
                self.c_chess.itemconfigure('square', state=tk.DISABLED)
            elif {'w+', 'b+', 'wf'} == set(all_player_pos) or {'w+', 'b+', 'bf'} == set(all_player_pos):
                self.game_still_going = False       # only king - king+knight left
                self.c_chess.itemconfigure('square', state=tk.DISABLED)
            elif {'w+', 'b+', 'wA', 'bA'} == set(all_player_pos) and \
                    self.pos_map_color(all_player_pos['wA']) == self.pos_map_color(all_player_pos['bA']):
                self.game_still_going = False       # only king+bishop - king+bishop left, with bishops on same color
                self.c_chess.itemconfigure('square', state=tk.DISABLED)

    def legal_move_possible(self, x):
        current_player_positions = [i for i in self.chess_board_keys if self.chess_board[i][0] == x]
        for self.position1 in current_player_positions:
            for self.position2 in self.chess_board_keys:
                if self.chess_board[self.position2] not in [x + 'T', x + 'f', x + 'A', x + '+', x + '*', x + 'i'] and \
                        self.check_legal_move() and not self.virtual_move_results_check(x):
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
                self.file_to_load = 'initial_setup.txt'


if __name__ == '__main__':
    root = tk.Tk()
    Chess(root)
    root.mainloop()
