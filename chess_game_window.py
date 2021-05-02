import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title('Chess Game')
screen_size = (1366, 768)
canvas_widgets_color = 'orange'
root.minsize(screen_size[0]-2, screen_size[1]-92)   # 2 blue edge, 50 bar and menu, 40 tray = 92
root.maxsize(screen_size[0]-2, screen_size[1]-92)
root.geometry(f'{screen_size[0]-2}x{screen_size[1]-92}+0+0')

root.option_add('*tearOff', False)
chess_menu = tk.Menu(root)
root['menu'] = chess_menu
file_menu = tk.Menu(chess_menu)
chess_menu.add_cascade(label='File', menu=file_menu, underline=0)
file_menu.add_command(label='Board size')

c_board_size = screen_size[1] - 100   # 92 plus 3 + 5
c_col2_width = screen_size[0] - c_board_size - 24   # 2 blue edge, 12 separator, 5,5 pad x
c_curr_plyr_h = c_board_size / 4
c_capt_h = (c_board_size - c_curr_plyr_h - 24) / 2   # 12 x 2 separator

c_board = tk.Canvas(root, width=c_board_size, height=c_board_size)
c_blck_capt = tk.Canvas(root, width=c_col2_width, height=c_capt_h)
c_whte_capt = tk.Canvas(root, width=c_col2_width, height=c_capt_h)
c_curr_plyr = tk.Canvas(root, width=c_col2_width, height=c_curr_plyr_h)
for canvas_item in [c_board, c_blck_capt, c_whte_capt, c_curr_plyr]:
    canvas_item['bg'] = canvas_widgets_color
    canvas_item['highlightthickness'] = 0
separator1 = ttk.Separator(root, orient='vertical')
separator2 = ttk.Separator(root, orient='horizontal')
separator3 = ttk.Separator(root, orient='horizontal')
c_board.grid(column=0, row=0, columnspan=1, rowspan=5, padx=5, pady=(3, 0))
separator1.grid(column=1, row=0, columnspan=1, rowspan=5, sticky='n, s')
c_blck_capt.grid(column=2, row=0, padx=(5, 0), pady=(3, 5))
separator2.grid(column=2, row=1, sticky='w, e')
c_curr_plyr.grid(column=2, row=2, padx=(5, 0), pady=5)
separator3.grid(column=2, row=3, sticky='w, e')
c_whte_capt.grid(column=2, row=4, padx=(5, 0), pady=(5, 0))

root.mainloop()
