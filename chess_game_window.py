import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title('Chess Game')
screen_size = (1366, 768)
root.minsize(screen_size[0]-2, screen_size[1]-92)   # 2 blue edge, 50 bar and menu, 40 tray = 92
root.maxsize(screen_size[0]-2, screen_size[1]-92)
root.geometry(f'{screen_size[0]-2}x{screen_size[1]-92}+0+0')

root.option_add('*tearOff', False)
chess_menu = tk.Menu(root)
root['menu'] = chess_menu
file_menu = tk.Menu(chess_menu)
chess_menu.add_cascade(label='File', menu=file_menu, underline=0)
file_menu.add_command(label='Board size')

cnv_brd_size = screen_size[1]-100   # 92 plus 3 + 5
cnv_capt_width = screen_size[0]-cnv_brd_size-24   # 2 blue edge, 12 separator, 5,5 pad x
cnv_capt_height = 5

cnv_brd = tk.Canvas(root, width=cnv_brd_size, height=cnv_brd_size, bg='orange', highlightthickness=0)
cnv_capt_b = tk.Canvas(root, width=cnv_capt_width, height=225, bg='orange', highlightthickness=0)
cnv_capt_w = tk.Canvas(root, width=cnv_capt_width, height=225, bg='orange', highlightthickness=0)
cnv_curr_plr = tk.Canvas(root, width=cnv_capt_width, height=194, bg='orange', highlightthickness=0)
separator1 = ttk.Separator(root, orient='vertical')
separator2 = ttk.Separator(root, orient='horizontal')
separator3 = ttk.Separator(root, orient='horizontal')
cnv_brd.grid(column=0, row=0, columnspan=1, rowspan=5, padx=5, pady=(3, 0))  # sticky=(N, S, E, W)
separator1.grid(column=1, row=0, columnspan=1, rowspan=5, sticky='n, s')
cnv_capt_b.grid(column=2, row=0, padx=(5, 0), pady=(3, 5))
separator2.grid(column=2, row=1, sticky='w, e')
cnv_curr_plr.grid(column=2, row=2, padx=(5, 0), pady=5)
separator3.grid(column=2, row=3, sticky='w, e')
cnv_capt_w.grid(column=2, row=4, padx=(5, 0), pady=(5, 0))






root.mainloop()
