import tkinter as tk
from time import strftime, gmtime

def light_theme():
    frame = tk.Frame(root, bg="white")
    frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)
    lbl_1 = tk.Label(frame, font=('calibri', 40, 'bold'),
                    background='white', foreground='black')
    lbl_1.pack(anchor="s")

    def time():
        string = strftime('%H:%M:%S')
        lbl_1.config(text=string)
        lbl_1.after(1000, time)
    time()

def dark_theme():
    frame = tk.Frame(root, bg="black")
    frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)
    lbl_2 = tk.Label(frame, font=('calibri', 40, 'bold'),
                    background='black', foreground='white')
    lbl_2.pack(anchor="s")

    def time():
        string = strftime('%H:%M:%S')
        lbl_2.config(text=string)
        lbl_2.after(1000, time)
    time()

root = tk.Tk()
root.title("Dijital Saat")
canvas = tk.Canvas(root, height=140, width=400)
canvas.pack()

frame = tk.Frame(root, bg='white')
frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)
lbl = tk.Label(frame, font=('calibri', 40, 'bold'),
                    background='white', foreground='black')
lbl.pack(anchor="s")

def time():
    string = strftime('%H:%M:%S')
    lbl.config(text=string)
    lbl.after(1000, time)
time()

menubar = tk.Menu(root)
theme_menu = tk.Menu(menubar, tearoff=0)
theme_menu.add_command(label="Açık Tema", command=light_theme)
theme_menu.add_command(label="Koyu Tema", command=dark_theme)
menubar.add_cascade(label="Tema", menu=theme_menu)
root.config(menu=menubar)

root.mainloop()
