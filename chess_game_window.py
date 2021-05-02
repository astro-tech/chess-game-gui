import tkinter as tk
from tkinter import ttk


class Chess:
    def __init__(self, master):
        self.master = master
        self.master.title('Chess Game')
        self.screen_size = (1366, 768)
        self.canvas_widgets_color = 'orange'
        self.master.minsize(self.screen_size[0]-2, self.screen_size[1]-92)   # 2blue edge,50bar and menu,40tray=92
        self.master.maxsize(self.screen_size[0]-2, self.screen_size[1]-92)
        self.master.geometry(f'{self.screen_size[0]-2}x{self.screen_size[1]-92}+0+0')

        self.create_menu()
        self.create_4_main_canvas()

    def create_menu(self):
        self.master.option_add('*tearOff', False)
        self.chess_menu = tk.Menu(self.master)
        self.master['menu'] = self.chess_menu
        self.file_menu = tk.Menu(self.chess_menu)
        self.chess_menu.add_cascade(label='File', menu=self.file_menu, underline=0)
        self.file_menu.add_command(label='Board size')

    def create_4_main_canvas(self):
        self.c_board_size = self.screen_size[1] - 100   # 92 plus 3 + 5
        self.c_col2_width = self.screen_size[0] - self.c_board_size - 24   # 2blue edge,12separator, 5,5 pad x
        self.c_curr_plyr_h = self.c_board_size / 4
        self.c_capt_h = (self.c_board_size - self.c_curr_plyr_h - 24) / 2   # 12 x 2 separator

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


if __name__ == '__main__':
    root = tk.Tk()
    Chess(root)
    root.mainloop()