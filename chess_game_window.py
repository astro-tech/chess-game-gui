import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import operator


def char_range(c1, c2):  # stackoverflow.com/questions/7001144/range-over-character-in-python
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2) + 1):
        yield chr(c)


def center(win, x_offset, y_offset):
    # stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    title_bar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + title_bar_height + frm_width
    win.geometry(f'+{win.winfo_screenwidth() // 2 - win_width // 2 - x_offset}'
                 f'+{win.winfo_screenheight() // 2 - win_height // 2 - y_offset}')


class GameWindow:
    def __init__(self, master, screen_size, file_to_load, from_menu):
        self.master = master
        self.master.title('GMF Chess')
        try:
            self.master.iconphoto(True, tk.PhotoImage(file='./graphics/chess_icon64.png'))  # True=top level inherits it
        except tk.TclError:
            print('Game icon file not found')
        self.screen_size = screen_size  # (1024, 576)(1366, 768)(1920, 1080)
        self.file_to_load = file_to_load
        self.menu_initiated_values = from_menu
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

        self.chess_board = {}  # game save values start
        self.captured_pieces = {}
        self.current_player = None
        self.current_player2 = None
        self.other_player = None
        self.these_rook_king_moved = []
        self.en_pass_pos = None
        self.number_of_player = None  # game save values end
        self.chess_board_keys = None
        self.chess_board_virtual = None
        self.c_chess = None
        self.currently_selected = tk.StringVar()
        self.show_legal_moves_man = tk.BooleanVar(value=True)
        self.show_legal_moves_computer = tk.BooleanVar(value=False)
        self.c = {}  # dictionary for gui elements created later and used for multiple methods
        self.bak = {}  # dictionary for backups
        self.position1 = None
        self.position2 = None
        self.selected_piece = None
        self.game_still_going = True
        self.winner = None
        self.castling_rook = None  # tempo info holder for castling
        self.king_position = None  # tempo info holder for castling
        self.piece_dgr = {}
        self.previous_12_board = {}
        self.game_is_saved = False
        self.game_speed = 1000

        self.start_new_game = True
        while self.start_new_game:
            self.play_game()

    def play_game(self):
        self.clear_previous_session()
        self.draw_menu()
        self.load_board_setup()
        self.display_board()  # legacy display in terminal
        self.draw_4_main_canvas()
        self.draw_chess_board()
        self.draw_captured_areas()
        self.draw_captured_pieces()
        self.draw_squares()
        self.draw_pieces()
        # center(self.master, 0, 18)
        self.master.focus_set()
        while self.game_still_going:
            if (self.number_of_player == 1 and self.current_player2 == 'man') or self.number_of_player == 2:
                self.handle_turn(self.current_player)
                if self.promotion_coordinate(self.current_player):
                    self.promotion_dialog(self.current_player)
            else:
                if self.number_of_player == 0:   # to leave time to finish rendering
                    self.master.after(self.game_speed * 3, lambda: self.currently_selected.set('demo'))
                    self.c_chess.wait_variable(self.currently_selected)
                if self.currently_selected.get() != 'exit':
                    self.computer_turn(self.current_player)
                    if self.promotion_coordinate(self.current_player):
                        self.computer_promotion(self.current_player)
            self.game_is_saved = False
            self.flip_player()
            self.check_if_game_still_going(self.current_player)
        self.ask_for_new_game()

    def clear_previous_session(self):
        self.game_still_going = True
        self.winner = None
        self.position1 = None   # this indicates first turn, see handle turn initialize select piece
        self.previous_12_board = {str(i) + 'ago': {} for i in range(1, 13)}
        for widget in self.master.winfo_children():
            print('destroying' + str(widget))
            widget.destroy()

    def draw_menu(self):
        def show_help():
            messagebox.showinfo(title='Help', message=instructions_text)
        self.master.option_add('*tearOff', False)
        main_menu = tk.Menu(self.master)
        self.master['menu'] = main_menu
        file_menu = tk.Menu(main_menu)
        options_menu = tk.Menu(main_menu)
        help_menu = tk.Menu(main_menu)
        main_menu.add_cascade(label='File', menu=file_menu, underline=0)
        main_menu.add_cascade(label='Options', menu=options_menu, underline=0)
        main_menu.add_cascade(label='Help', menu=help_menu, underline=0)
        file_menu.add_command(label='New Game', command=self.new_game)
        file_menu.add_command(label='Load Game', command=self.load_game)
        file_menu.add_command(label='Save Game', command=self.save_game)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.exit_game)
        options_menu.add_command(label='Settings', command=self.settings_dialog)
        help_menu.add_command(label='About', command=show_help)

        self.c['castling_menu'] = tk.Menu(self.master)  # context menu
        self.c['castling_menu'].add_command(label='Castling', command=self.castling)

        self.master.protocol("WM_DELETE_WINDOW", lambda: self.exit_game())  # intercepting close button

    def new_game(self):
        new_response = tk.messagebox.askyesno(title='New game', message='Do you want to start new game?')
        if new_response:
            if self.number_of_player != 2:  # to leave time to finish rendering
                self.master.after(self.game_speed * 2, lambda: self.currently_selected.set('demo'))
                self.c_chess.wait_variable(self.currently_selected)
            self.game_still_going = False
            self.file_to_load = 'initial_setup.txt'
            self.menu_initiated_values['current_player'] = 'w'  # too keep these preferences
            self.menu_initiated_values['current_player2'] = 'man'
            self.menu_initiated_values['other_player'] = 'b'
            self.menu_initiated_values['number_of_player'] = self.number_of_player
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
            file.write('number_of_player=' + str(self.number_of_player))
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
                if self.save_game():  # user didn't click on cancel, otherwise no exit
                    exiting()
            else:
                exiting()

    def settings_dialog(self):
        show_legal_moves_man2 = tk.BooleanVar(value=self.show_legal_moves_man.get())
        show_legal_moves_cmp2 = tk.BooleanVar(value=self.show_legal_moves_computer.get())
        number_of_player2 = tk.IntVar(value=self.number_of_player)
        settings_selected = tk.BooleanVar()

        settings_window = tk.Toplevel(self.master)
        settings_window.focus_set()
        settings_window.title('Settings')
        settings_window.resizable(False, False)
        settings_window.protocol("WM_DELETE_WINDOW", lambda: settings_selected.set(True))

        settings_frame = ttk.Frame(settings_window, padding=10)
        settings_frame.grid(column=0, row=0, sticky='n, w, e, s')

        self.c['msg0'] = ttk.Label(settings_frame, text='Dual player mode (man-man):', padding=5)
        self.c['msg1'] = ttk.Label(settings_frame, text='Single player mode (man-computer):', padding=5)
        self.c['msg2'] = ttk.Label(settings_frame, text='No player mode (computer-computer) for demo:', padding=5)
        self.c['msg3'] = ttk.Label(settings_frame, text='Highlight legal movement squares for player:', padding=5)
        self.c['msg4'] = ttk.Label(settings_frame, text='Highlight legal movement squares for computer:', padding=5)
        self.c['button0'] = ttk.Radiobutton(settings_frame, variable=number_of_player2, value=2, padding=5)
        self.c['button1'] = ttk.Radiobutton(settings_frame, variable=number_of_player2, value=1, padding=5)
        self.c['button2'] = ttk.Radiobutton(settings_frame, variable=number_of_player2, value=0, padding=5)
        self.c['button3'] = \
            ttk.Checkbutton(settings_frame, variable=show_legal_moves_man2, onvalue=True, offvalue=False, padding=5)
        self.c['button4'] = \
            ttk.Checkbutton(settings_frame, variable=show_legal_moves_cmp2, onvalue=True, offvalue=False, padding=5)
        for i in [0, 1, 2, 3, 4]:
            self.c['msg' + str(i)].grid(column=0, row=i, columnspan=3, sticky='n, w')
            self.c['button' + str(i)].grid(column=3, row=i, sticky='n, e')

        def apply_button_logic():
            self.show_legal_moves_man.set(show_legal_moves_man2.get())
            self.show_legal_moves_computer.set(show_legal_moves_cmp2.get())
            self.number_of_player = number_of_player2.get()
            settings_selected.set(True)

        apply_button = ttk.Button(settings_frame, text='Apply', command=apply_button_logic)
        cancel_button = ttk.Button(settings_frame, text='Cancel', command=lambda: settings_selected.set(True))
        apply_button.grid(column=2, row=5, sticky='n, e, s')
        cancel_button.grid(column=3, row=5, sticky='n, s')

        self.master.wait_variable(settings_selected)
        settings_window.destroy()

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
            self.number_of_player = int(data[102].split('=')[1])
            file.close()
            self.chess_board_keys = list(self.chess_board.keys())
            if self.menu_initiated_values and self.file_to_load == 'initial_setup.txt':
                self.current_player = self.menu_initiated_values['current_player']
                self.current_player2 = self.menu_initiated_values['current_player2']
                self.other_player = self.menu_initiated_values['other_player']
                self.number_of_player = self.menu_initiated_values['number_of_player']
        except FileNotFoundError as error:
            print(error)
            tk.messagebox.showerror(title='Error', message='initial_setup.txt is missing from game directory!')
            self.master.destroy()
        except IndexError:
            print('Game file is corrupted!')
            tk.messagebox.showerror(title='Error', message='Game file is corrupted!')
            self.chess_board = self.bak['chess_board'].copy()  # restoring backups
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

    @staticmethod
    def txt_map_piece(txt):
        if txt == 'T':
            return '???'
        elif txt == 'f':
            return '???'
        elif txt == 'A':
            return '???'
        elif txt == '+':
            return '???'
        elif txt == '*':
            return '???'
        elif txt == 'i':
            return '???'

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
                if self.coord_danger_from(self.king_position, self.chess_board, self.current_player) or \
                        self.coord_danger_from('f' + self.king_position[1], self.chess_board, self.current_player) or \
                        self.coord_danger_from('g' + self.king_position[1], self.chess_board, self.current_player):
                    return False
            elif self.castling_rook[0] == 'a':
                if self.coord_danger_from(self.king_position, self.chess_board, self.current_player) or \
                        self.coord_danger_from('d' + self.king_position[1], self.chess_board, self.current_player) or \
                        self.coord_danger_from('c' + self.king_position[1], self.chess_board, self.current_player):
                    return False
            return True

        def modify_rook_king(color):
            rook_id = self.c_chess.find_withtag(f'piece_{self.castling_rook}')
            self.c_chess.itemconfigure(rook_id, fill=self.txt_map_color(self.current_player)[color])
            king_id = self.c_chess.find_withtag(f'piece_{self.king_position}')
            self.c_chess.itemconfigure(king_id, fill=self.txt_map_color(self.current_player)[color])
            return rook_id, king_id  # also extracts object id

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

        def gui_castling(color, k_col):  # moving and updating tag
            self.c_chess.coords(modify_rook_king(0)[0],  # setting color back together with return id
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
                    self.en_pass_pos = ['  ', '  ']     # to clear previous en passant possibilities
                    self.currently_selected.set('exit')  # to bypass anticipated position1 and flip player
                    self.display_board()
            else:
                modify_rook_king(0)

    def en_passant(self, x):
        if self.current_player2 == 'man':
            curr_speed = 0
        else:
            curr_speed = self.game_speed
        if self.chess_board[self.position1][1] == 'i' and self.position2 == self.en_pass_pos[0]:
            first_empty_slot = self.captured_pieces[self.other_player].index('  ')
            self.captured_pieces[self.other_player][first_empty_slot] = self.chess_board[self.en_pass_pos[1]]
            # copy captured piece to captured canvas
            self.master.after(curr_speed * 2, lambda player=self.other_player: self.c['captured'][player].itemconfigure(
                    self.c['captured'][player].find_withtag('captured_' + str(first_empty_slot)),
                    text=self.txt_map_piece('i')))
            # get id of captured piece
            captured_piece = self.c_chess.find_withtag(f'piece_{self.en_pass_pos[1]}')
            print('En passant! captured id=' + str(captured_piece))
            # delete captured piece from chess board
            self.master.after(curr_speed * 2, lambda: self.c_chess.delete(captured_piece))
            self.chess_board[self.en_pass_pos[1]] = '  '
        if x == 'w':
            if self.chess_board[self.position1][1] == 'i' and self.position1[1] == '2' and self.position2[1] == '4':
                self.en_pass_pos[0] = self.position2[0] + str(3)
                self.en_pass_pos[1] = self.position2
            else:
                self.en_pass_pos = ['  ', '  ']
        elif x == 'b':
            if self.chess_board[self.position1][1] == 'i' and self.position1[1] == '7' and self.position2[1] == '5':
                self.en_pass_pos[0] = self.position2[0] + str(6)
                self.en_pass_pos[1] = self.position2
            else:
                self.en_pass_pos = ['  ', '  ']
        if self.en_pass_pos != ['  ', '  ']:
            print(f'En passant possible for {self.en_pass_pos[1]}, capture at {self.en_pass_pos[0]}')

    def display_next_player(self, x):
        if self.current_player2 == 'man' and self.number_of_player == 1 and self.position1 and \
                self.currently_selected.get() != 'reset':
            curr_speed = self.game_speed
        else:
            curr_speed = 0
        if x == 'w':
            print('White is next to move')
            self.master.after(curr_speed * 2, lambda:
                              self.c['right_center'].itemconfigure(self.c['current_player_label'],
                                                                   text='White is next to move'))
        elif x == 'b':
            print('Black is next to move')
            self.master.after(curr_speed * 2, lambda:
                              self.c['right_center'].itemconfigure(self.c['current_player_label'],
                                                                   text='Black is next to move'))
        return curr_speed

    def handle_turn(self, x):
        # print(self.position1)
        self.selected_piece = None
        curr_speed = self.display_next_player(x)    # also returns current game speed
        self.c_chess.itemconfigure('piece', state=tk.DISABLED)  # initialize select piece
        self.c_chess.itemconfigure('square', state=tk.DISABLED)
        self.master.after(curr_speed * 2, lambda: self.c_chess.itemconfigure(x, state=tk.NORMAL))
        print('waiting for position1')
        self.c_chess.wait_variable(self.currently_selected)
        if self.currently_selected.get() != 'exit':  # if user didn't close program meanwhile
            self.position1 = self.currently_selected.get()
            print('position1=' + self.position1)
            self.selected_piece = self.c_chess.find_withtag(f'piece_{self.position1}')  # get id of selected piece
            print('id=' + str(self.selected_piece[0]))
            self.c_chess.itemconfigure(self.selected_piece, fill=self.txt_map_color(x)[1])  # set constant red

            self.c_chess.itemconfigure('piece', state=tk.DISABLED)  # initialize select square
            valid_position2s = self.generate_valid_position2(x)  # activate only valid movement squares
            if self.show_legal_moves_man.get():
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
                    self.c_chess.dtag(self.selected_piece, f'piece_{self.position1}')  # update tag of piece
                    self.c_chess.addtag(f'piece_{self.position2}', 'withtag', self.selected_piece)
                    print('new tags=' + str(self.c_chess.gettags(self.selected_piece)))
                    for i in valid_position2s:  # set squares to original color
                        self.c_chess.itemconfigure('square_' + i, fill=self.pos_map_color(i)[0])
                else:
                    tk.messagebox.showwarning(title='Illegal move',
                                              message='Movement leaves or places the king in check!')
                    self.reset_selection()
                self.c_chess.itemconfigure('square', state=tk.DISABLED)
                self.display_board()

    def computer_turn(self, x):
        values = {'+': 10, '*': 9, 'T': 5, 'A': 3, 'f': 3, 'i': 1}
        ops = {'>': operator.gt, '<': operator.lt, '>=': operator.ge, '<=': operator.le}

        def rank_piece_dgr(d_dict):  # returns coordinates of pieces in d_dict ranked in descending values
            val_assign_piece_dgr = {key: values[d_dict[key][1]] for key in d_dict}
            ranked_piece_dgr = \
                [piece for i in range(10, 0, -1) for piece in val_assign_piece_dgr if i == val_assign_piece_dgr[piece]]
            return ranked_piece_dgr

        def attack_worth(dictionary, comp):
            if len(self.piece_dgr[dictionary]) == 1 or dictionary == 'oth':
                if ops[comp](values[self.chess_board[self.position1][1]],
                             values[self.chess_board[self.position2][1]]):
                    return True
            else:
                if ops[comp](values[self.chess_board[self.position1][1]],
                             values[self.piece_dgr[dictionary][rank_piece_dgr(self.piece_dgr[dictionary])[0]][1]]):
                    return True
            return False

        def piece_dgr_values_check(board1, board2, player, comp):
            dgr_values_before = [values[board1[i][1]] for i in self.chess_board_keys if board1[i][0] == player and
                                 self.coord_danger_from(i, board1, player)]
            dgr_values_after = [values[board2[i][1]] for i in self.chess_board_keys if board2[i][0] == player and
                                self.coord_danger_from(i, board2, player)]
            # print(dgr_values_before, end=',')
            # print(dgr_values_after, end=',')
            # print(player + ',' + str(ops[comp](sum(dgr_values_before), sum(dgr_values_after))))
            return {'r': ops[comp](sum(dgr_values_before), sum(dgr_values_after)),
                    'b': sum(dgr_values_before), 'a': sum(dgr_values_after)}

        def measure_dist(pos1, pos2):
            x_dist = abs(ord(pos2[0]) - ord(pos1[0]))
            y_dist = abs(int(pos2[1]) - int(pos1[1]))
            dist = (x_dist ** 2 + y_dist ** 2) ** 0.5
            return float(round(dist, 1))

        self.display_next_player(x)
        strategy = 'None'
        strategy_found = False
        print("It's computer's turn. Analyzing chess board...")
        curr_player_pos = [i for i in self.chess_board_keys if self.chess_board[i][0] == x]
        print("Computer's pieces standing on: " + str(curr_player_pos))
        self.piece_dgr['cur'] = \
            {i: self.chess_board[i] for i in curr_player_pos if self.coord_danger_from(i, self.chess_board, x)}
        print("Computer's pieces under attack: " + str(self.piece_dgr['cur']))
        if self.piece_dgr['cur']:  # if under attack: strategies (1, 2, 3, 4)
            print('Pieces in danger ranked: ' + str(rank_piece_dgr(self.piece_dgr['cur'])))
            for cur_pos in rank_piece_dgr(self.piece_dgr['cur']):   # iterates through the ordered list of pieces in dgr
                # identifies the present piece's attacker and attacks it
                self.position2 = self.coord_danger_from(cur_pos, self.chess_board, x)
                # seeks a legal move to capture the attacker on a safe place (1st)
                for self.position1 in curr_player_pos:
                    if self.check_legal_move() and not self.virtual_move_results_check(x) and \
                            not self.coord_danger_from(self.position2, self.chess_board, x):
                        strategy_found = True
                        strategy = '1: Defense attack to safe place'
                        break
                else:
                    # if not found, it tries to capture the attacker on a non-safe place if attack worth (2nd)
                    for self.position1 in curr_player_pos:
                        if self.check_legal_move() and not self.virtual_move_results_check(x) and \
                                attack_worth('cur', '<'):
                            strategy_found = True
                            strategy = '2: Defense attack to non-safe place if worth it (loosing lower value piece)'
                            break
                    else:
                        # if not found, it tries to retreat from the threatened coordinate (it checks virtual movement
                        # as well due to possible blocking of attacker on current position) so that the sum of values
                        # of pieces in danger don't increase (3rd)
                        self.position1 = cur_pos
                        randomized_chess_board_keys = random.sample(self.chess_board_keys, len(self.chess_board_keys))
                        for self.position2 in randomized_chess_board_keys:
                            if self.chess_board[self.position2] not in \
                                    [x + 'T', x + 'f', x + 'A', x + '+', x + '*', x + 'i'] \
                                    and self.check_legal_move() and not self.virtual_move_results_check(x) and \
                                    not self.coord_danger_from(self.position2, self.chess_board_virtual, x) and \
                                    not self.move_danger_from_en_passant(self.chess_board) and \
                                    piece_dgr_values_check(self.chess_board, self.chess_board_virtual, x, '>=')['r']:
                                strategy_found = True
                                strategy = '3: Retreating to safe place'
                                break
                        else:
                            # if not found, it tries once more to capture the attacker on a non-safe place if attack
                            # worth, but this time losing a same value piece is accepted (4th)
                            self.position2 = self.coord_danger_from(cur_pos, self.chess_board, x)
                            for self.position1 in curr_player_pos:
                                if self.check_legal_move() and not self.virtual_move_results_check(x) and \
                                        attack_worth('cur', '<='):
                                    strategy_found = True
                                    strategy = '4: Defense attack to non-safe place if worth it ' \
                                               '(loosing same value piece)'
                                    break
                            else:
                                continue
                break
        # the following was moved out of if statement, due later usage and medium warning
        oth_player_pos = [i for i in self.chess_board_keys if self.chess_board[i][0] == self.other_player]
        if not strategy_found:  # if not under attack or move not found, it tries to attack (5, 6, 7)
            print("Opponent's pieces standing on: " + str(oth_player_pos))
            self.piece_dgr['oth'] = {i: self.chess_board[i] for i in oth_player_pos if
                                     self.coord_danger_from(i, self.chess_board, self.other_player)}
            print("Opponent's pieces under attack: " + str(self.piece_dgr['oth']))
            if self.piece_dgr['oth']:
                # iterates through the ordered list of other player's pieces in danger
                for oth_pos in rank_piece_dgr(self.piece_dgr['oth']):
                    # it checks which current player piece endangers the present other player's piece
                    self.position1 = self.coord_danger_from(oth_pos, self.chess_board, self.other_player)
                    self.position2 = oth_pos    # tries to attack to safe place (5th)
                    if self.check_legal_move() and not self.virtual_move_results_check(x) and \
                            not self.coord_danger_from(self.position2, self.chess_board, x):
                        strategy_found = True
                        strategy = '5: Attack to safe place'
                        break
                    # if not managed, it still tries the attack if it worth (6th)
                    elif self.check_legal_move() and not self.virtual_move_results_check(x) and \
                            attack_worth('oth', '<'):
                        strategy_found = True
                        strategy = '6: Attack to non-safe place if worth it'
                        break
        # if not under attack or move not found, it tries the en passant capture (7th)
        if not strategy_found and self.en_pass_pos[0] != '  ':
            self.position1 = self.coord_danger_from(self.en_pass_pos[0], self.chess_board, self.other_player)
            if self.position1 and self.chess_board[self.position1][1] == 'i':
                self.position2 = self.en_pass_pos[0]
                strategy_found = True
                strategy = '7: Attack with En passant'
        # if not under attack or previous moves not found, it tries to move to safe place towards opponent's king
        # so that the sum of values of current pieces in danger don't increase, but the opponent's value increases
        # as much as possible (8th)
        if not strategy_found:
            safe_position2s = [i for i in self.chess_board_keys if not self.coord_danger_from(i, self.chess_board, x)
                               and self.chess_board[i] not in [x + 'T', x + 'f', x + 'A', x + '+', x + '*', x + 'i']]
            oth_king_pos = None
            for i in self.chess_board_keys:
                if self.chess_board[i] == self.other_player + '+':
                    oth_king_pos = i
            dist_add_pos2s = {pos: measure_dist(oth_king_pos, pos) for pos in safe_position2s}
            dist_ordered_pos2s = [pos for i in range(1, 101) for pos in dist_add_pos2s if dist_add_pos2s[pos] == i / 10]
            randomized_curr_player_pos = random.sample(curr_player_pos, len(curr_player_pos))
            # now it checks if strategy 8 is needed, otherwise only draw happens
            oth_values_before = sum([values[self.chess_board[i][1]] for i in oth_player_pos])
            if oth_values_before > 13:
                eight = {}
                for self.position1 in randomized_curr_player_pos:
                    for self.position2 in dist_ordered_pos2s:
                        if self.check_legal_move() and not self.virtual_move_results_check(x) and \
                                piece_dgr_values_check(self.chess_board, self.chess_board_virtual, x, '>=')['r'] and \
                                not self.move_danger_from_en_passant(self.chess_board):
                            eight[(self.position1, self.position2)] = piece_dgr_values_check(   # value assign to moves
                                self.chess_board, self.chess_board_virtual, self.other_player, '<')['a']
                sorted_eight = sorted(eight.items(), key=lambda i: i[1], reverse=True)
                # if eight still empty, returns []
                if sorted_eight and sorted_eight[0][1] > piece_dgr_values_check(    # if greatest value after > before
                        self.chess_board, self.chess_board_virtual, self.other_player, '<')['b']:
                    strategy_found = True
                    strategy = '8: Move to safe place, try to prepare future attack'
                    self.position1 = sorted_eight[0][0][0]
                    self.position2 = sorted_eight[0][0][1]
                # print(sorted_eight)
            else:
                print('Strategy 8 deactivated due to low threat from opponent')
            # tries once more, but without increasing the the sum of value of the opponent's pieces in danger (9th)
            if not strategy_found:
                for self.position1 in randomized_curr_player_pos:
                    for self.position2 in dist_ordered_pos2s:
                        if self.check_legal_move() and not self.virtual_move_results_check(x) and \
                                piece_dgr_values_check(self.chess_board, self.chess_board_virtual, x, '>=')['r'] and \
                                not self.move_danger_from_en_passant(self.chess_board):
                            strategy_found = True
                            strategy = '9: Move to safe place'
                            break
                    else:
                        continue
                    break
        # if previous strategies failed, it tries any legal move (10th)
        if not strategy_found:
            randomized_curr_player_pos = random.sample(curr_player_pos, len(curr_player_pos))
            randomized_chess_board_keys = random.sample(self.chess_board_keys, len(self.chess_board_keys))
            for self.position1 in randomized_curr_player_pos:
                for self.position2 in randomized_chess_board_keys:
                    if self.chess_board[self.position2] not in [x + 'T', x + 'f', x + 'A', x + '+', x + '*', x + 'i'] \
                            and self.check_legal_move() and not self.virtual_move_results_check(x):
                        strategy = '10: Make any legal move'
                        break
                else:
                    continue
                break
        print('Strategy ' + strategy)
        print('Moving from: ' + self.position1)
        print('Moving to: ' + self.position2)
        self.en_passant(x)
        if self.chess_board[self.position2] != '  ':
            captured = self.chess_board[self.position2]
            first_empty_slot = self.captured_pieces[self.other_player].index('  ')
            self.captured_pieces[self.other_player][first_empty_slot] = self.chess_board[self.position2]
            self.master.after(
                self.game_speed * 2, lambda player=self.other_player:
                self.c['captured'][player].itemconfigure(
                    self.c['captured'][player].find_withtag('captured_' + str(first_empty_slot)),
                    text=self.txt_map_piece(captured[1])))
            captured_piece = self.c_chess.find_withtag(f'piece_{self.position2}')
            print('Capture! captured id=' + str(captured_piece))
            self.master.after(self.game_speed * 2, lambda: self.c_chess.delete(captured_piece))

        if self.show_legal_moves_computer.get():
            position2 = self.position2
            valid_position2s = self.generate_valid_position2(x)
            for i in valid_position2s:
                self.master.after(self.game_speed, lambda pos=i: self.c_chess.itemconfigure(
                    'square_' + pos, fill=self.pos_map_color(pos)[2]))
                self.master.after(self.game_speed * 2, lambda pos=i: self.c_chess.itemconfigure(
                    'square_' + pos, fill=self.pos_map_color(pos)[0]))
            self.position2 = position2

        self.chess_board[self.position2] = self.chess_board[self.position1]
        self.chess_board[self.position1] = '  '
        selected_piece = self.c_chess.find_withtag(f'piece_{self.position1}')  # get id of selected piece
        print('Move with id=' + str(selected_piece[0]))
        self.master.after(self.game_speed,
                          lambda: self.c_chess.itemconfigure(selected_piece, fill=self.txt_map_color(x)[1]))  # set red
        self.master.after(self.game_speed * 2,
                          lambda pos=self.position2: self.c_chess.coords(selected_piece, self.get_square_center(pos)))
        self.master.after(self.game_speed * 2,
                          lambda: self.c_chess.itemconfigure(selected_piece, fill=self.txt_map_color(x)[0]))  # set orig
        print('old tags=' + str(self.c_chess.gettags(selected_piece)))
        self.c_chess.dtag(selected_piece, f'piece_{self.position1}')  # update tag of piece
        self.c_chess.addtag(f'piece_{self.position2}', 'withtag', selected_piece)
        print('new tags=' + str(self.c_chess.gettags(selected_piece)))
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
            if (self.number_of_player == 1 and self.current_player2 == 'man') or \
                    self.number_of_player == 0:
                self.current_player2 = 'computer'
            elif (self.number_of_player == 1 and self.current_player2 == 'computer') or \
                    self.number_of_player == 2:
                self.current_player2 = 'man'
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
        promotion_window.focus_set()
        promotion_window.title('Promotion')
        promotion_window.resizable(False, False)
        promotion_window.protocol("WM_DELETE_WINDOW", lambda: promotion_selected.set(True))

        promotion_frame = ttk.Frame(promotion_window, padding=10)
        promotion_frame.grid(column=0, row=0, sticky='n, w, e, s')

        message = ttk.Label(promotion_frame,
                            text="One of your pawn reached 8th rank.\nChoose a replacement piece from the list:")
        message.grid(column=0, row=0, columnspan=4, sticky='n, w, s')

        buttons = {}  # creating radio buttons to select pieces
        for piece, label in [('*', 'Queen (???)'), ('T', 'Rook (???)'), ('A', 'Bishop (???)'), ('f', 'Knight (???)')]:
            buttons[piece] = ttk.Radiobutton(promotion_frame, text=label, variable=button_value, value=piece,
                                             padding=10)
        for piece, col in [('*', 0), ('T', 1), ('A', 2), ('f', 3)]:
            buttons[piece].grid(column=col, row=1, sticky='n, w, e, s')

        ok_button = ttk.Button(promotion_frame, text='Select', command=lambda: promotion_selected.set(True))
        ok_button.grid(column=3, row=2, sticky='n, w, e, s')

        self.master.wait_variable(promotion_selected)
        promotion_window.destroy()

        self.chess_board[self.promotion_coordinate(x)] = x + button_value.get()  # set backend
        self.c_chess.itemconfigure(self.selected_piece, text=self.txt_map_piece(button_value.get()))  # set frontend
        self.display_board()

    def computer_promotion(self, x):
        promotion_piece = self.c_chess.find_withtag(f'piece_{self.promotion_coordinate(x)}')
        self.master.after(self.game_speed * 2,
                          lambda: self.c_chess.itemconfigure(promotion_piece, text=self.txt_map_piece('*')))
        self.chess_board[self.promotion_coordinate(x)] = x + '*'
        print('Promotion occurred. ' + x + 'i became ' + x + '*.')
        self.display_board()

    def check_legal_move(self):
        if self.chess_board[self.position1][1] == 'T':  # Rook
            if self.check_movement_cols_rows() and self.check_obstacle_cols_rows():
                return True
        if self.chess_board[self.position1][1] == 'A':  # Bishop
            if self.check_movement_diagonals() and self.check_obstacle_diagonals():
                return True
        if self.chess_board[self.position1][1] == '*':  # Queen
            if (self.check_movement_cols_rows() or self.check_movement_diagonals()) \
                    and (self.check_obstacle_cols_rows() or self.check_obstacle_diagonals()):
                return True
        if self.chess_board[self.position1][1] == '+':  # King
            if abs(ord(self.position2[0]) - ord(self.position1[0])) < 2 and \
                    abs(int(self.position2[1]) - int(self.position1[1])) < 2:
                return True
        if self.chess_board[self.position1][1] == 'f':  # Knight
            if (abs(ord(self.position2[0]) - ord(self.position1[0])) == 1 and
                abs(int(self.position2[1]) - int(self.position1[1])) == 2) or \
                    (abs(ord(self.position2[0]) - ord(self.position1[0])) == 2 and
                     abs(int(self.position2[1]) - int(self.position1[1])) == 1):
                return True
        if self.chess_board[self.position1] == 'wi':  # Pawn white
            if self.move_one_capture_side_one(-1) or self.first_move_two(2, 3, -2):
                return True
        if self.chess_board[self.position1] == 'bi':  # Pawn black
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

    def move_one_capture_side_one(self, dct1):  # direction up if -1, down if 1
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

    def first_move_two(self, init_row, m_row, dct2):  # for white: init_row=2, next_row=3, direction=-2
        if int(self.position1[1]) == init_row and self.chess_board[self.position2] == '  ' and \
                self.chess_board[self.position2[0] + str(m_row)] == '  ' and \
                self.position1[0] == self.position2[0] and int(self.position1[1]) - int(self.position2[1]) == dct2:
            return True
        return False

    def virtual_move_results_check(self, x):
        self.chess_board_virtual = self.chess_board.copy()  # shallow copy
        self.chess_board_virtual[self.position2] = self.chess_board_virtual[self.position1]
        self.chess_board_virtual[self.position1] = '  '
        return self.king_in_check(x, self.chess_board_virtual)

    # checks if xn coordinate of x player on board is under attack from enemy and returns enemy's coordinates
    def coord_danger_from(self, xn, board, x):
        queen_rook = self.coord_danger_from_queen_rook_bishop(
            xn, board, x, [('z', 1, 0, -1), ('z', 8, 0, 1), ('h', 9, 1, 0), ('a', 9, -1, 0)], ('*', 'T'))
        # check_param order: from xn checking down, up, right, left
        if queen_rook:
            return queen_rook
        queen_bishop = self.coord_danger_from_queen_rook_bishop(
            xn, board, x, [('h', 1, 1, -1), ('h', 8, 1, 1), ('a', 8, -1, 1), ('a', 1, -1, -1)], ('*', 'A'))
        # check_param order: from xn checking right down, right up, left up, left down
        if queen_bishop:
            return queen_bishop
        king = self.coord_danger_from_king_knight(xn, board, x, [(-1, -1), (0, -1), (1, -1), (-1, 0),
                                                                 (1, 0), (-1, 1), (0, 1), (1, 1)], '+')
        if king:
            return king
        knight = self.coord_danger_from_king_knight(xn, board, x, [(1, -2), (2, -1), (2, 1), (1, 2),
                                                                   (-1, 2), (-2, 1), (-2, -1), (-1, -2)], 'f')
        if knight:
            return knight
        white_pawn = self.coord_danger_from_pawn(xn, board, [(-1, -1), (1, -1)], 'w')
        if white_pawn and x == 'b':
            return white_pawn
        black_pawn = self.coord_danger_from_pawn(xn, board, [(-1, 1), (1, 1)], 'b')
        if black_pawn and x == 'w':
            return black_pawn

    @staticmethod
    def coord_danger_from_queen_rook_bishop(xn, board, x, check_param, pieces):

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
        attacker = None
        for cur, oth in [('w', 'b'), ('b', 'w')]:
            if x == cur:
                for i in threat_coordinates:
                    if board[i] == oth + pieces[0]:
                        attacker = i
                if not attacker:
                    for i in threat_coordinates:
                        if board[i] == oth + pieces[1]:
                            attacker = i
        return attacker

    def coord_danger_from_king_knight(self, xn, board, x, xy, piece):
        possible_coordinates = [chr(ord(xn[0]) + a) + str(int(xn[1]) + b) for a, b in xy]
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
        possible_coordinates = [chr(ord(xn[0]) + a) + str(int(xn[1]) + b) for a, b in xy]
        threat_coordinates = list(set(possible_coordinates).intersection(set(self.chess_board_keys)))
        for i in threat_coordinates:
            if board[i] == color + 'i':
                return i

    def move_danger_from_en_passant(self, board):
        def check(cur, pos1, pos2, oth):
            if board[self.position1] == cur and self.position1[1] == pos1 and self.position2[1] == pos2:
                possible_coordinates = [chr(ord(self.position2[0]) + a) + self.position2[1] for a in [1, -1]]
                threat_coordinates = list(set(possible_coordinates).intersection(set(self.chess_board_keys)))
                for i in threat_coordinates:
                    if board[i] == oth:
                        return i
        attacker = check('wi', '2', '4', 'bi')
        if not attacker:
            attacker = check('bi', '7', '5', 'wi')
        return attacker

    def check_if_game_still_going(self, x):
        if self.currently_selected.get() != 'exit':
            legal_move = self.legal_move_possible(x)  # to prevent running the method twice
            all_player_pos = {self.chess_board[i]: i for i in self.chess_board_keys if self.chess_board[i] != '  '}
            if not legal_move and self.king_in_check(x, self.chess_board):  # checkmate
                self.game_still_going = False
                self.winner = self.other_player
            elif not legal_move:  # stalemate
                self.game_still_going = False
            # other stalemates:
            elif {'w+', 'b+'} == set(all_player_pos):
                self.game_still_going = False  # only king - king left
            elif {'w+', 'b+', 'wA'} == set(all_player_pos) or {'w+', 'b+', 'bA'} == set(all_player_pos):
                self.game_still_going = False  # only king - king+bishop left
            elif {'w+', 'b+', 'wf'} == set(all_player_pos) or {'w+', 'b+', 'bf'} == set(all_player_pos):
                self.game_still_going = False  # only king - king+knight left
            elif {'w+', 'b+', 'wA', 'bA'} == set(all_player_pos) and \
                    self.pos_map_color(all_player_pos['wA']) == self.pos_map_color(all_player_pos['bA']):
                self.game_still_going = False  # only king+bishop - king+bishop left, with bishops on same color
            if self.chess_board == self.previous_12_board['4ago'] and \
                    self.chess_board == self.previous_12_board['8ago'] and \
                    self.chess_board == self.previous_12_board['12ago']:
                self.game_still_going = False   # the same board repeated for 3x times
            for a, b in list(zip([i for i in range(12, 1, -1)], [i for i in range(11, 0, -1)])):    # (12, 11) to (2, 1)
                self.previous_12_board[str(a) + 'ago'] = self.previous_12_board[str(b) + 'ago'].copy()
            self.previous_12_board['1ago'] = self.chess_board.copy()

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


instructions_text = """Instructions:\n
To start the game, select from the 3 available window sizes below. If you select Load Game, the previously selected \
number of player preference is also loaded. With selecting the New Game option you have to chose between man-computer \
or man-man modes. Selecting the first one also prompts to chose the man's piece color. The single/dual player mode can \
be changed during gameplay, always taking effect from the next turn.\nTo select a piece, click on it with left mouse \
button, to deselect it, right click or hit Esc. For castling, right click on the rook which will be involved in \
castling. Note that castling will not be offered if the selected rook or it's king moved already.\nThe game supports \
special moves like en-passant or pawn promotion. If one of the pawn reaches 8th rank, an option will be offered to \
replace it.\nAt any time during the game you can access New/Load/Save Game from File Menu.\nThe Options/Settings \
Menu let's you to change number of player and if the legal move squares to be highlighted or not.\nDuring gameplay \
there can be warning messages in case the king is left in check.\nAt the end the winner color or draw is displayed \
and a new game is offered.\nIt's time to Get More Freedom!\nCopyright by Csaba Bai ??2020-2021"""

if __name__ == '__main__':
    root = tk.Tk()
    GameWindow(root, (1024, 576), 'initial_setup.txt', {})
    # root.mainloop()
