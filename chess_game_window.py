import tkinter as tk
from tkinter import ttk


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
        self.screen_size = (1366, 768)  # other (1024, 576)(1366, 768)(1920, 1080)
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
        self.piece_size = int(self.square_size * (5 / 7))   # 50 for 1366x768
        self.light_piece_color = '#d2ac79'
        self.light_piece_highlight = '#f4541e'
        self.dark_piece_color = '#2a1510'
        self.dark_piece_highlight = '#ca2e04'
        # font parameters
        self.font_size = int(self.square_size / 3.5)  # 20 for 1366x768
        self.font_color = 'black'
        self.font_type = 'TKDefaultFont'
        # chess backend variables
        self.chess_board = {}
        self.captured_pieces = {}
        self.current_player = None
        self.other_player = None
        self.currently_selected = tk.StringVar()
        self.selected_piece = None
        self.position1 = '  '
        self.position2 = '  '
        self.game_still_going = True

        self.play_game()

    def play_game(self):
        self.load_board_setup('initial_setup.txt')
        self.draw_menu()
        self.draw_4_main_canvas()
        self.draw_chess_board()
        self.draw_captured()
        self.draw_squares()
        self.initialize_pieces()    # draw included
        self.play_dual()

    def load_board_setup(self, filename):
        file = open(filename, 'r')
        data = file.read().splitlines()
        for line in data[0:64]:
            (key, value) = line.split('=')
            self.chess_board[key] = value   # importing full chess board data (old generate board)
        for color in ['w', 'b']:
            self.captured_pieces[color] = []
        for line in data[65:81]:
            value = line.split('=')[1]
            self.captured_pieces['w'].append(value)     # importing captures white pieces data
        for line in data[81:97]:
            value = line.split('=')[1]
            self.captured_pieces['b'].append(value)     # importing captures black pieces data
        current_player_line = data[97]
        current_player_value = current_player_line.split('=')[1]
        self.current_player = current_player_value
        other_player_line = data[98]
        other_player_value = other_player_line.split('=')[1]
        self.other_player = other_player_value
        file.close()
        self.chess_keys = list(self.chess_board.keys())

    def draw_menu(self):
        self.master.option_add('*tearOff', False)
        self.chess_menu = tk.Menu(self.master)
        self.master['menu'] = self.chess_menu
        self.file_menu = tk.Menu(self.chess_menu)
        self.chess_menu.add_cascade(label='File', menu=self.file_menu, underline=0)
        self.file_menu.add_command(label='Board size')

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

        self.master.bind('<Button-3>', lambda e: self.reset_selection())

    def draw_chess_board(self):
        self.c_123abc_w = (self.c_left_side - self.square_size * 8) / 2    # strip width of 1-8, a-h

        self.c_chess = tk.Canvas(self.c_left, width=self.square_size * 8, height=self.square_size * 8,
                                 bg=self.canvas_widgets_color)

        self.board_abcx2 = {}   # creating two rows of letters a-h
        for i in ['n', 's']:
            self.board_abcx2[i] = tk.Canvas(self.c_left, width=self.square_size * 8,
                                            height=self.c_123abc_w, bg=self.abc123_color)
            for j in char_range('a', 'h'):
                self.board_abcx2[i].create_text(
                    self.square_size * (ord(j)-96.5), self.c_123abc_w / 2,
                    text=j, fill=self.font_color, font=(self.font_type, self.font_size))

        self.board_123x2 = {}   # creating two columns of numbers 1-8
        for i in ['w', 'e']:
            self.board_123x2[i] = tk.Canvas(self.c_left, width=self.c_123abc_w,
                                            height=self.c_left_side, bg=self.abc123_color)
            for j in range(0, 8):
                self.board_123x2[i].create_text(
                    self.c_123abc_w / 2, self.c_left_side - self.c_123abc_w - self.square_size * (j + 0.5),
                    text=j+1, fill=self.font_color, font=(self.font_type, self.font_size))

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
                                          height=self.square_size * 2, bg='orange', highlightthickness=0)
        for color, y in [('b', self.square_size), ('w', self.c_right_top_height - self.square_size * 3)]:
            self.c_captured[color].place(anchor='n', height=self.square_size * 2, width=self.square_size * 8,
                                         x=self.c_right_width / 2, y=y)

    def draw_squares(self):
        for i in self.chess_keys:
            x0 = (ord(i[0]) - 97) * self.square_size
            y0 = abs(int(i[1]) - 8) * self.square_size
            x1 = (ord(i[0]) - 96) * self.square_size
            y1 = abs(int(i[1]) - 9) * self.square_size
            if (ord(i[0]) + int(i[1])) % 2 == 0:    # True if dark square, False if light square
                color = self.dark_squares_color
                act_color = self.dark_squares_highlight
            else:
                color = self.light_squares_color
                act_color = self.light_squares_highlight
            self.c_chess.create_rectangle(x0, y0, x1, y1, fill=color, width=0,
                                          activefill=act_color, tag=('square', 'square_' + i))
            # e not used but always created as event, so a new kw parameter n is created which is local to lambda
            self.c_chess.tag_bind('square_' + i, '<Button-1>', lambda e, n=i: self.currently_selected.set(n))

    def get_center(self, tag):
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
        for i in self.chess_board:
            if self.chess_board[i] != '  ':
                if self.chess_board[i][0] == 'w':
                    self.draw_pieces(i, 'w')
                elif self.chess_board[i][0] == 'b':
                    self.draw_pieces(i, 'b')
            # all tags has to be bound, otherwise not able to move piece after initial move
            self.c_chess.tag_bind('piece_' + i, '<Button-1>', lambda e, n=i: self.currently_selected.set(n))

    def draw_pieces(self, pos, color):
        self.c_chess.create_text(
            self.get_center(pos),
            text=self.txt_map_piece(self.chess_board[pos][1]),
            tag=('piece', 'piece_' + pos, color),
            fill=self.txt_map_color(color)[0],
            activefill=self.txt_map_color(color)[1],
            font=(self.font_type, self.piece_size))

    def play_dual(self):
        while self.game_still_going:
            self.handle_turn(self.current_player)
            self.flip_player()

    def handle_turn(self, x):
        if x == 'w':
            print('White is next to move')     # todo make it a canvas text
        elif x == 'b':
            print('Black is next to move')

        self.c_chess.itemconfigure('piece', state=tk.DISABLED)      # initialize select piece
        self.c_chess.itemconfigure('square', state=tk.DISABLED)
        self.c_chess.itemconfigure(x, state=tk.NORMAL)
        print('waiting for position1')
        self.c_chess.wait_variable(self.currently_selected)
        self.position1 = self.currently_selected.get()
        print('position1=' + self.position1)
        self.selected_piece = self.c_chess.find_withtag(f'piece_{self.position1}')   # get id of selected piece
        print('id=' + str(self.selected_piece))
        self.c_chess.itemconfigure(self.selected_piece, fill=self.txt_map_color(x)[1])     # set constant red

        self.c_chess.itemconfigure('piece', state=tk.DISABLED)      # initialize select square
        self.c_chess.itemconfigure('square', state=tk.NORMAL)
        print('waiting for position2')
        # in this timeframe there's possibility to reset selection
        self.c_chess.wait_variable(self.currently_selected)
        if self.selected_piece is not None:
            self.position2 = self.currently_selected.get()
            print('position2=' + self.position2)
            self.c_chess.coords(self.selected_piece, self.get_center(self.position2))    # movement of piece
            self.c_chess.itemconfigure(self.selected_piece, fill=self.txt_map_color(x)[0])  # set original color
            print('old tags=' + str(self.c_chess.gettags(self.selected_piece)))
            self.c_chess.itemconfigure(self.selected_piece,
                                       tag=('piece', f'piece_{self.position2}', x))     # update tag of piece
            print('new tags=' + str(self.c_chess.gettags(self.selected_piece)))
            self.selected_piece = None

    def reset_selection(self):
        print('reset callback working')
        if self.selected_piece is not None:
            self.c_chess.itemconfigure(self.selected_piece, fill=self.txt_map_color(self.current_player)[0])
            self.selected_piece = None
            self.currently_selected.set('reset')    # substitute anticipated position2 with a reset flag

    def flip_player(self):
        if self.currently_selected.get() != 'reset':
            if self.current_player == 'w':
                self.current_player = 'b'
                self.other_player = 'w'
            elif self.current_player == 'b':
                self.current_player = 'w'
                self.other_player = 'b'
        else:
            print('reset occurred, not flipping player')


if __name__ == '__main__':
    root = tk.Tk()
    Chess(root)
    root.mainloop()
