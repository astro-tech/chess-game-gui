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
        self.screen_size = (1024, 576)  # other (1024, 576)(1366, 768)(1920, 1080)
        # 2 blue edge, 50 bar and menu, 40 tray = 92
        self.master.minsize(self.screen_size[0] - 2, self.screen_size[1] - 92)
        self.master.maxsize(self.screen_size[0] - 2, self.screen_size[1] - 92)
        self.master.geometry(f'{self.screen_size[0] - 2}x{self.screen_size[1] - 92}+0+0')

        self.square_size = int(self.screen_size[1] / 10.97)  # 70 for 1366x768
        self.canvas_widgets_color = 'grey75'
        self.abc123_color = 'grey50'
        self.dark_squares_color = 'grey25'
        self.light_squares_color = 'grey95'
        self.dark_squares_highlight = '#800000'
        self.light_squares_highlight = '#ffc8c8'
        self.font_type = 'TKDefaultFont'
        self.font_size = int(self.square_size / 3.5)  # 20 for 1366x768
        self.font_color = 'black'

        self.create_menu()
        self.create_4_main_canvas()
        self.create_chess_board()
        self.create_squares()

    def create_menu(self):
        self.master.option_add('*tearOff', False)
        self.chess_menu = tk.Menu(self.master)
        self.master['menu'] = self.chess_menu
        self.file_menu = tk.Menu(self.chess_menu)
        self.chess_menu.add_cascade(label='File', menu=self.file_menu, underline=0)
        self.file_menu.add_command(label='Board size')

    def create_4_main_canvas(self):
        self.c_board_size = self.screen_size[1] - 100  # 92 plus 3 + 5
        self.c_col2_width = self.screen_size[0] - self.c_board_size - 24  # 2blue edge,12separator, 5,5 pad x
        self.c_curr_plyr_h = self.c_board_size / 4
        self.c_capt_h = (self.c_board_size - self.c_curr_plyr_h - 24) / 2  # 12 x 2 separator

        self.c_board = tk.Canvas(self.master, width=self.c_board_size, height=self.c_board_size)
        self.c_blck_capt = tk.Canvas(self.master, width=self.c_col2_width, height=self.c_capt_h)
        self.c_whte_capt = tk.Canvas(self.master, width=self.c_col2_width, height=self.c_capt_h)
        self.c_curr_plyr = tk.Canvas(self.master, width=self.c_col2_width, height=self.c_curr_plyr_h)
        for canvas_item in [self.c_board, self.c_blck_capt, self.c_whte_capt, self.c_curr_plyr]:
            canvas_item['bg'] = self.canvas_widgets_color
            canvas_item['highlightthickness'] = 0
        self.separator1 = ttk.Separator(self.master, orient='vertical')
        self.separator2 = ttk.Separator(self.master, orient='horizontal')
        self.separator3 = ttk.Separator(self.master, orient='horizontal')

        self.c_board.grid(column=0, row=0, columnspan=1, rowspan=5, padx=5, pady=(3, 0))
        self.separator1.grid(column=1, row=0, columnspan=1, rowspan=5, sticky='n, s')
        self.c_blck_capt.grid(column=2, row=0, padx=(5, 0), pady=(3, 5))
        self.separator2.grid(column=2, row=1, sticky='w, e')
        self.c_curr_plyr.grid(column=2, row=2, padx=(5, 0), pady=5)
        self.separator3.grid(column=2, row=3, sticky='w, e')
        self.c_whte_capt.grid(column=2, row=4, padx=(5, 0), pady=(5, 0))

    def create_chess_board(self):
        self.c_123abc_w = (self.c_board_size - self.square_size * 8) / 2    # strip width of 1-8, a-h

        self.c_chess = tk.Canvas(self.c_board, width=self.square_size * 8, height=self.square_size * 8,
                                 bg=self.canvas_widgets_color)

        self.board_abcx2 = {}   # creating two rows of letters a-h
        for i in ['n', 's']:
            self.board_abcx2[i] = tk.Canvas(self.c_board, width=self.square_size * 8,
                                            height=self.c_123abc_w, bg=self.abc123_color)
            for j in char_range('a', 'h'):
                self.board_abcx2[i].create_text(
                    self.square_size * (ord(j)-96.5), self.c_123abc_w / 2,
                    text=j, fill=self.font_color, font=(self.font_type, self.font_size))

        self.board_123x2 = {}   # creating two columns of numbers 1-8
        for i in ['w', 'e']:
            self.board_123x2[i] = tk.Canvas(self.c_board, width=self.c_123abc_w,
                                            height=self.c_board_size, bg=self.abc123_color)
            for j in range(0, 8):
                self.board_123x2[i].create_text(
                    self.c_123abc_w / 2, self.c_board_size - self.c_123abc_w - self.square_size * (j + 0.5),
                    text=j+1, fill=self.font_color, font=(self.font_type, self.font_size))

        for canvas_item in [self.c_chess, self.board_abcx2['n'], self.board_abcx2['s'],
                            self.board_123x2['w'], self.board_123x2['e']]:
            canvas_item['highlightthickness'] = 0

        self.board_123x2['w'].grid(column=0, row=0, rowspan=3)
        self.board_abcx2['n'].grid(column=1, row=0)
        self.c_chess.grid(column=1, row=1)
        self.board_abcx2['s'].grid(column=1, row=2)
        self.board_123x2['e'].grid(column=2, row=0, rowspan=3)

    def create_squares(self):
        self.chess_keys = []
        for number in range(8, 0, -1):
            for letter in char_range('a', 'h'):
                self.chess_keys.append(letter + str(number))
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
                                          activefill=act_color, tag=('square', i))
            # e not used but always created as event, so a new kw parameter n is created which is local to lambda
            self.c_chess.tag_bind(i, '<Button-1>', lambda e, n=i: print(n))

        self.c_chess.itemconfigure('square', state=tk.DISABLED)
        self.master.after(4000, lambda: self.c_chess.itemconfigure('square', state=tk.NORMAL))


if __name__ == '__main__':
    root = tk.Tk()
    Chess(root)
    root.mainloop()
