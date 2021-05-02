import tkinter as tk
from tkinter import ttk, filedialog
from chess_game_window import GameWindow, instructions_text, center


class GameMenu:
    def __init__(self, master):
        self.master = master
        self.master.title('GMF Chess')
        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", lambda: self.simple_exit())
        try:
            self.master.iconphoto(True, tk.PhotoImage(file='./graphics/chess_icon64.png'))  # True=top level inherits it
            self.banner = tk.PhotoImage(file='./graphics/chess_banner.png')
        except tk.TclError:
            print('Game icon/image files not found')
            self.banner = None
        self.screen_sizes = [(1024, 576), (1366, 768), (1920, 1080)]
        self.menu_initiated_values = {}
        self.m = {}
        self.file_to_load = 'initial_setup.txt'

        self.draw_main()
        center(self.master, 0, 100)
        self.start_pressed = tk.BooleanVar()
        self.master.wait_variable(self.start_pressed)   # chess_game_window_initiation_from_here

        self.screen_size = self.screen_sizes[self.m['resolution'].get()]
        print(self.screen_size)
        print(self.menu_initiated_values)
        print(self.file_to_load)
        if self.start_pressed.get():
            self.game_window = tk.Toplevel(self.master)
            self.master.withdraw()
            GameWindow(self.game_window, self.screen_size, self.file_to_load, self.menu_initiated_values)

    def draw_main(self):
        top_frame = ttk.Frame(self.master, padding=(10, 10, 10, 0))
        top_frame.grid(column=0, row=0, sticky='n, w, e, s')
        welcome_label = ttk.Label(
            top_frame, text='Welcome to GMF Chess!', padding=(40, 30), font='TKDefaultFont', relief='ridge')
        welcome_label.grid(column=0, row=0, columnspan=2, sticky='n, s')
        if self.banner:
            welcome_label['padding'] = 0
            welcome_label['image'] = self.banner
        textbox = tk.Text(top_frame, width=41, height=10, font='TkMenuFont', bg='grey90', wrap='word')
        textbox.insert('1.0', instructions_text)
        textbox['state'] = 'disabled'
        textbox.grid(column=0, row=1, sticky='n, w, s, e')
        textbox_scroll = ttk.Scrollbar(top_frame, orient='vertical', command=textbox.yview)
        textbox['yscrollcommand'] = textbox_scroll.set
        textbox_scroll.grid(column=1, row=1, sticky='n, w, s, e')
        screen_label = ttk.Label(top_frame, text='Select game window size:', padding=5)
        screen_label.grid(column=0, row=2, sticky='e, w')

        bottom_frame = ttk.Frame(self.master, padding=(10, 0, 10, 10))
        bottom_frame.grid(column=0, row=1, sticky='n, w, e, s')
        self.m['resolution'] = tk.IntVar(value=0)
        for res, val in [('1024x576 ', 0), ('1366x768 ', 1), ('1920x1080', 2)]:
            self.m['res_button_' + str(val)] = ttk.Radiobutton(bottom_frame, text=res, variable=self.m['resolution'],
                                                               value=val, padding=(9, 0, 9, 10))
            self.m['res_button_' + str(val)].grid(column=val, row=0, sticky='n, s')
        self.m['new_button'] = ttk.Button(bottom_frame, text='New Game', command=self.new_game_dialog)
        self.m['new_button'].grid(column=0, row=1, sticky='n, s', pady=5)
        self.m['load_button'] = ttk.Button(bottom_frame, text='Load Game', command=self.load_game_dialog)
        self.m['load_button'].grid(column=1, row=1, sticky='n, s', pady=5)
        self.m['exit_button'] = ttk.Button(bottom_frame, text='Exit', command=self.simple_exit)
        self.m['exit_button'].grid(column=2, row=1, sticky='n, s', pady=5)

    def simple_exit(self):
        self.master.destroy()
        self.start_pressed.set(False)

    def show_help(self):
        self.master.deiconify()
        for widget in ['res_button_0', 'res_button_1', 'res_button_2', 'new_button', 'load_button']:
            self.m[widget]['state'] = 'disabled'
        self.m['exit_button']['text'] = 'OK'
        self.m['exit_button']['command'] = lambda: self.master.withdraw()
        self.master.protocol("WM_DELETE_WINDOW", lambda: self.master.withdraw())

    def new_game_dialog(self):
        chosen_color = tk.StringVar(value='w')
        number_of_player2 = tk.IntVar()
        new_game_selected = tk.BooleanVar()

        new_game_window = tk.Toplevel(self.master)
        new_game_window.focus_set()
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
            if 'message2' in self.m:
                self.m['message2'].destroy()
                self.m['start_button'].destroy()
            self.m['message2'] = ttk.Label(new_game_frame, text='Choose piece color:', padding=5)
            self.m['message2'].grid(column=0, row=2, columnspan=2, sticky='n, s')
            self.m['white_button'] = ttk.Radiobutton(new_game_frame, text='White',
                                                     variable=chosen_color, value='w', padding=(80, 0, 0, 5))
            self.m['black_button'] = ttk.Radiobutton(new_game_frame, text='Black',
                                                     variable=chosen_color, value='b', padding=(30, 0, 0, 5))
            self.m['white_button'].grid(column=0, row=3, sticky='n, w')
            self.m['black_button'].grid(column=1, row=3, sticky='n, w')
            self.m['start_button'] = ttk.Button(new_game_frame, text='Start!', command=start_button_logic)
            self.m['start_button'].grid(column=1, row=4, sticky='n, e, s')

        def draw_two():
            if 'message2' in self.m:
                self.m['message2'].destroy()
                self.m['start_button'].destroy()
                self.m['white_button'].destroy()
                self.m['black_button'].destroy()
            self.m['message2'] = ttk.Label(new_game_frame, text='White moves first.', padding=5)
            self.m['message2'].grid(column=0, row=2, columnspan=2, sticky='n, s')
            self.m['start_button'] = ttk.Button(new_game_frame, text='Start!', command=start_button_logic)
            self.m['start_button'].grid(column=1, row=3, sticky='n, e, s')

        def start_button_logic():
            self.menu_initiated_values['number_of_player'] = number_of_player2.get()
            if chosen_color.get() == 'w':
                self.menu_initiated_values['current_player'] = 'w'
                self.menu_initiated_values['current_player2'] = 'man'
                self.menu_initiated_values['other_player'] = 'b'
            else:
                self.menu_initiated_values['current_player'] = 'b'
                self.menu_initiated_values['current_player2'] = 'computer'
                self.menu_initiated_values['other_player'] = 'w'
            new_game_selected.set(True)
            self.start_pressed.set(True)

        self.master.wait_variable(new_game_selected)
        new_game_window.destroy()

    def load_game_dialog(self):
        path = tk.filedialog.askopenfilename(filetypes=[('Text Documents', '*.txt')])
        if path:
            self.file_to_load = path
            self.start_pressed.set(True)


if __name__ == '__main__':
    root = tk.Tk()
    GameMenu(root)
    # root.mainloop()
