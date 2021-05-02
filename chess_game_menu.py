import tkinter as tk
from tkinter import ttk, filedialog


# https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
def center(win, x_offset, y_offset):
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    title_bar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + title_bar_height + frm_width
    win.geometry(f'+{win.winfo_screenwidth() // 2 - win_width // 2 - x_offset}'
                 f'+{win.winfo_screenheight() // 2 - win_height // 2 - y_offset}')


class Chess:
    def __init__(self, master):
        self.master = master
        self.master.title('Game Menu')
        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", lambda: self.simple_exit())
        #self.screen_size = None  # other (1024, 576)(1366, 768)(1920, 1080)
        self.screen_sizes = [(1024, 576), (1366, 768), (1920, 1080)]

        self.number_of_player = tk.IntVar()
        self.current_player2 = None
        self.c = {}
        self.file_to_load = None

        self.draw_main()
        center(self.master, 0, 100)
        self.start_pressed = tk.BooleanVar()
        self.master.wait_variable(self.start_pressed)
        self.screen_size = self.screen_sizes[self.c['resolution'].get()]

        print(self.screen_size)
        print(self.current_player2)
        print(self.number_of_player.get())
        if self.start_pressed.get():
            self.master.withdraw()
            self.configure_main_w()
            self.draw_menu()
            self.create_4_main_canvas()

    def draw_main(self):
        top_frame = ttk.Frame(self.master, padding=(10, 10, 10, 0))
        top_frame.grid(column=0, row=0, sticky='n, w, e, s')
        welcome_label = ttk.Label(
            top_frame, text='Welcome to Chess Game!', padding=(40, 30), font='TKDefaultFont', relief='ridge')
        welcome_label.grid(column=0, row=0, columnspan=2, sticky='n, s')
        textbox = tk.Text(top_frame, width=41, height=10, font='TkMenuFont', bg='grey90', wrap='word')
        my_text = """Instructions:\n
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
and a new game is offered.\nCopyright by Csaba Bai ©2020-2021"""
        textbox.insert('1.0', my_text)
        textbox['state'] = 'disabled'
        textbox.grid(column=0, row=1, sticky='n, w, s, e')
        textbox_scroll = ttk.Scrollbar(top_frame, orient='vertical', command=textbox.yview)
        textbox['yscrollcommand'] = textbox_scroll.set
        textbox_scroll.grid(column=1, row=1, sticky='n, w, s, e')
        screen_label = ttk.Label(top_frame, text='Select game window size:', padding=5)
        screen_label.grid(column=0, row=2, sticky='e, w')

        bottom_frame = ttk.Frame(self.master, padding=(10, 0, 10, 10))
        bottom_frame.grid(column=0, row=1, sticky='n, w, e, s')
        self.c['resolution'] = tk.IntVar(value=0)
        for res, val in [('1024x576 ', 0), ('1366x768 ', 1), ('1920x1080', 2)]:
            self.c['res_button_' + str(val)] = ttk.Radiobutton(bottom_frame, text=res, variable=self.c['resolution'],
                                                               value=val, padding=(9, 0, 9, 10))
            self.c['res_button_' + str(val)].grid(column=val, row=0, sticky='n, s')
        self.c['new_button'] = ttk.Button(bottom_frame, text='New Game', command=self.new_game_dialog)
        self.c['new_button'].grid(column=0, row=1, sticky='n, s', pady=5)
        self.c['load_button'] = ttk.Button(bottom_frame, text='Load Game', command=self.load_game_dialog)
        self.c['load_button'].grid(column=1, row=1, sticky='n, s', pady=5)
        self.c['exit_button'] = ttk.Button(bottom_frame, text='Exit', command=self.simple_exit)
        self.c['exit_button'].grid(column=2, row=1, sticky='n, s', pady=5)

    def simple_exit(self):
        self.master.destroy()
        self.start_pressed.set(False)

    def show_help(self):
        self.master.deiconify()
        for widget in ['res_button_0', 'res_button_1', 'res_button_2', 'new_button', 'load_button']:
            self.c[widget]['state'] = 'disabled'
        self.c['exit_button']['text'] = 'OK'
        self.c['exit_button']['command'] = lambda: self.master.withdraw()
        self.master.protocol("WM_DELETE_WINDOW", lambda: self.master.withdraw())

    def new_game_dialog(self):
        chosen_color = tk.StringVar(value='w')
        number_of_player2 = tk.IntVar()
        new_game_selected = tk.BooleanVar()

        new_game_window = tk.Toplevel(self.master)
        new_game_window.protocol("WM_DELETE_WINDOW", lambda: new_game_selected.set(True))
        new_game_window.grab_set()
        new_game_window.title('New Game')
        new_game_window.resizable(False, False)
        new_game_frame = ttk.Frame(new_game_window, padding=10)
        new_game_frame.grid(column=0, row=0, sticky='n, w, e, s')
        message1 = ttk.Label(new_game_frame, text='Choose number of player:', padding=5)
        message1.grid(column=0, row=0, columnspan=2, sticky='n, w')
        one_button = ttk.Radiobutton(new_game_frame, text='Single player (man-computer)',
                                     variable=number_of_player2, value=1, padding=5)
        two_button = ttk.Radiobutton(new_game_frame, text='Dual player (man-man)',
                                     variable=number_of_player2, value=2, padding=5)
        one_button.grid(column=0, row=1, sticky='n, w')
        two_button.grid(column=1, row=1, sticky='n, w')
        one_button.bind('<Button-1>', lambda e: draw_one())
        two_button.bind('<Button-1>', lambda e: draw_two())

        def draw_one():
            if 'message2' in self.c:
                self.c['message2'].destroy()
                self.c['start_button'].destroy()
            self.c['message2'] = ttk.Label(new_game_frame, text='Choose piece color:', padding=5)
            self.c['message2'].grid(column=0, row=2, columnspan=2, sticky='n, s')
            self.c['white_button'] = ttk.Radiobutton(new_game_frame, text='White',
                                                     variable=chosen_color, value='w', padding=(80, 0, 0, 5))
            self.c['black_button'] = ttk.Radiobutton(new_game_frame, text='Black',
                                                     variable=chosen_color, value='b', padding=(30, 0, 0, 5))
            self.c['white_button'].grid(column=0, row=3, sticky='n, w')
            self.c['black_button'].grid(column=1, row=3, sticky='n, w')
            self.c['start_button'] = ttk.Button(new_game_frame, text='Start!', command=start_button_logic)
            self.c['start_button'].grid(column=1, row=4, sticky='n, e, s')

        def draw_two():
            if 'message2' in self.c:
                self.c['message2'].destroy()
                self.c['start_button'].destroy()
                self.c['white_button'].destroy()
                self.c['black_button'].destroy()
            self.c['message2'] = ttk.Label(new_game_frame, text='White moves first.', padding=5)
            self.c['message2'].grid(column=0, row=2, columnspan=2, sticky='n, s')
            self.c['start_button'] = ttk.Button(new_game_frame, text='Start!', command=start_button_logic)
            self.c['start_button'].grid(column=1, row=3, sticky='n, e, s')

        def start_button_logic():
            self.number_of_player.set(number_of_player2.get())
            self.file_to_load = 'initial_setup.txt'
            if chosen_color.get() == 'w':
                self.current_player2 = 'man'
            else:
                self.current_player2 = 'computer'
            new_game_selected.set(True)
            self.start_pressed.set(True)

        self.master.wait_variable(new_game_selected)
        new_game_window.destroy()

    def load_game_dialog(self):
        path = tk.filedialog.askopenfilename(filetypes=[('Text Documents', '*.txt')])
        if path:
            self.file_to_load = path
            self.start_pressed.set(True)

    def configure_main_w(self):
        self.main_w = tk.Toplevel(self.master)
        self.main_w.title('Game Window')
        self.main_w.minsize(self.screen_size[0] - 2, self.screen_size[1] - 92)
        self.main_w.maxsize(self.screen_size[0] - 2, self.screen_size[1] - 92)
        self.main_w.geometry(f'{self.screen_size[0] - 2}x{self.screen_size[1] - 92}+0+0')

    def draw_menu(self):
        self.master.option_add('*tearOff', False)
        main_menu = tk.Menu(self.main_w)
        self.main_w['menu'] = main_menu
        file_menu = tk.Menu(main_menu)
        options_menu = tk.Menu(main_menu)
        help_menu = tk.Menu(main_menu)
        main_menu.add_cascade(label='File', menu=file_menu, underline=0)
        main_menu.add_cascade(label='Options', menu=options_menu, underline=0)
        main_menu.add_cascade(label='Help', menu=help_menu, underline=0)
        file_menu.add_command(label='New Game')
        file_menu.add_command(label='Load Game')
        file_menu.add_command(label='Save Game')
        file_menu.add_separator()
        file_menu.add_command(label='Exit')
        options_menu.add_command(label='Settings')
        help_menu.add_command(label='About', command=self.show_help)

    def create_4_main_canvas(self):
        self.c_board_size = self.screen_size[1] - 100   # 92 plus 3 + 5
        self.c_col2_width = self.screen_size[0] - self.c_board_size - 24   # 2blue edge,12separator, 5,5 pad x
        self.c_curr_plyr_h = self.c_board_size / 4
        self.c_capt_h = (self.c_board_size - self.c_curr_plyr_h - 24) / 2   # 12 x 2 separator

        self.c_board = tk.Canvas(self.main_w, width=self.c_board_size, height=self.c_board_size)
        self.c_blck_capt = tk.Canvas(self.main_w, width=self.c_col2_width, height=self.c_capt_h)
        self.c_whte_capt = tk.Canvas(self.main_w, width=self.c_col2_width, height=self.c_capt_h)
        self.c_curr_plyr = tk.Canvas(self.main_w, width=self.c_col2_width, height=self.c_curr_plyr_h)
        for canvas_item in [self.c_board, self.c_blck_capt, self.c_whte_capt, self.c_curr_plyr]:
            canvas_item['bg'] = 'orange'
            canvas_item['highlightthickness'] = 0
        self.separator1 = ttk.Separator(self.main_w, orient='vertical')
        self.separator2 = ttk.Separator(self.main_w, orient='horizontal')
        self.separator3 = ttk.Separator(self.main_w, orient='horizontal')
        self.c_board.grid(column=0, row=0, columnspan=1, rowspan=5, padx=5, pady=(3, 0))
        self.separator1.grid(column=1, row=0, columnspan=1, rowspan=5, sticky='n, s')
        self.c_blck_capt.grid(column=2, row=0, padx=(5, 0), pady=(3, 5))
        self.separator2.grid(column=2, row=1, sticky='w, e')
        self.c_curr_plyr.grid(column=2, row=2, padx=(5, 0), pady=5)
        self.separator3.grid(column=2, row=3, sticky='w, e')
        self.c_whte_capt.grid(column=2, row=4, padx=(5, 0), pady=(5, 0))
        center(self.main_w, 0, 18)


if __name__ == '__main__':
    root = tk.Tk()
    Chess(root)
    root.mainloop()
