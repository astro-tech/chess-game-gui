import tkinter as tk
from tkinter import ttk


class Chess:
    def __init__(self, master):
        self.master = master
        self.master.title('Chess Game')
        self.screen_size = (1366, 768)
        self.square_size = int(self.screen_size[1] / 10.97)  # 70 for 1366x768
        self.canvas_widgets_color = 'grey75'
        self.dark_squares_color = 'grey25'
        self.light_squares_color = 'grey95'
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
                                 bg=self.dark_squares_color)
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

        """This code generates the white squares over the grey canvas. This requires a list consisting of
        32 items, each consisting of 4 items, reprensenting the coordinates to create each rectange(x0, y0, x1, y1).
        To generate this list, it was neccessary to split it into two lists (coordinates leading each row,
        coordinates following this to fill the row. To generate the leading coordinates the initial lead_coords
        is given (the top left rectangle's coordinates). Then it is divided if the row number (0-7) is odd or
        even. For odd rows we always add the increment, fo even rows we alternate subtraction and addition.
        (-, +, -, +). Once we have the leading rectangles's coordinates, we do a nested loop to generate the
        remaining 3 coordinates in each row. This is the follow_coords = [] (initially empty). The outer loop
        generates the row number (0-7), and the inner loop generates the 3 required increments. Finally the
        lead and follow lists are added together and the full list whites_coords can be used. It is destructured
        with *i when each rectangle coordinate is needed.      
        """

        #  initially in a list of 1 element consisting of 4 numbers
        self.lead_coords = [[0, 0, self.square_size, self.square_size]]
        for i in range(1, 8):
            if i % 2 == 1:
                self.lead_coords.append([self.lead_coords[i - 1][0] + self.square_size,
                                         self.lead_coords[i - 1][1] + self.square_size,
                                         self.lead_coords[i - 1][2] + self.square_size,
                                         self.lead_coords[i - 1][3] + self.square_size])
            elif i % 2 == 0:
                self.lead_coords.append([self.lead_coords[i - 1][0] - self.square_size,
                                         self.lead_coords[i - 1][1] + self.square_size,
                                         self.lead_coords[i - 1][2] - self.square_size,
                                         self.lead_coords[i - 1][3] + self.square_size])
        self.follow_coords = []
        for i in range(0, 8):
            for j in [self.square_size*2, self.square_size*4, self.square_size*6]:
                self.follow_coords.append([self.lead_coords[i][0] + j, self.lead_coords[i][1],
                                           self.lead_coords[i][2] + j, self.lead_coords[i][3]])
        self.whites_coords = self.lead_coords + self.follow_coords
        for i in self.whites_coords:
            self.c_chess.create_rectangle(*i, fill=self.light_squares_color, width=0, activefill='#ffc8c8',
                                          tag='checker')

        self.c_chess.addtag('a8', 'withtag', 1)
        self.c_chess.tag_bind('a8', '<Button-1>', lambda e: print('a8'))
        self.c_chess.itemconfigure('checker', state=tk.DISABLED)
        self.master.after(5000, lambda: self.c_chess.itemconfigure('checker', state=tk.NORMAL))



if __name__ == '__main__':
    root = tk.Tk()
    Chess(root)
    root.mainloop()
