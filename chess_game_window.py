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
        self.square_size = int(self.screen_size[1] / 10.97)  # 70 for 1366x768
        self.canvas_widgets_color = 'grey75'
        self.dark_squares_color = 'grey25'
        self.light_squares_color = 'grey95'
        self.dark_squares_highlight = '#800000'
        self.light_squares_highlight = '#ffc8c8'
        self.color_abc = 'grey50'
        self.color_123 = 'grey55'
        self.master.minsize(self.screen_size[0] - 2, self.screen_size[1] - 92)  # 2blue edge,50bar and menu,40tray=92
        self.master.maxsize(self.screen_size[0] - 2, self.screen_size[1] - 92)
        self.master.geometry(f'{self.screen_size[0] - 2}x{self.screen_size[1] - 92}+0+0')

        self.create_menu()
        self.create_4_main_canvas()
        self.create_chess_board()

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
        self.c_chess = tk.Canvas(self.c_board, width=self.square_size * 8, height=self.square_size * 8,
                                 bg=self.canvas_widgets_color)
        self.board_abc_n = tk.Canvas(self.c_board, width=self.square_size * 8,
                                     height=(self.c_board_size - self.square_size * 8) / 2, bg=self.color_abc)
        self.board_abc_s = tk.Canvas(self.c_board, width=self.square_size * 8,
                                     height=(self.c_board_size - self.square_size * 8) / 2, bg=self.color_abc)
        self.board_123_w = tk.Canvas(self.c_board, width=(self.c_board_size - self.square_size * 8) / 2,
                                     height=self.c_board_size, bg=self.color_123)
        self.board_123_e = tk.Canvas(self.c_board, width=(self.c_board_size - self.square_size * 8) / 2,
                                     height=self.c_board_size, bg=self.color_123)
        for canvas_item in [self.c_chess, self.board_abc_n, self.board_abc_s, self.board_123_w, self.board_123_e]:
            canvas_item['highlightthickness'] = 0
        self.board_123_w.grid(column=0, row=0, rowspan=3)
        self.board_abc_n.grid(column=1, row=0)
        self.c_chess.grid(column=1, row=1)
        self.board_abc_s.grid(column=1, row=2)
        self.board_123_e.grid(column=2, row=0, rowspan=3)

        # create_squares
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



if __name__ == '__main__':
    root = tk.Tk()
    Chess(root)
    root.mainloop()
