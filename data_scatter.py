import time
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import dataset

MARKER = "*"  # ID 70216990 -> 7 -> star

NUM_COLS = [c for c in dataset.df.columns
            if c not in dataset.CATEGORICAL_COLS]

x_col, y_col = NUM_COLS[0], NUM_COLS[1]

root = tk.Tk()
fig = Figure(figsize=(6, 4))
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

def draw():
    ax.clear()
    ax.scatter(dataset.df[x_col], dataset.df[y_col], marker=MARKER)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    canvas.draw()

def make_setter(axis):
    def set_col(col):
        global x_col, y_col
        if axis == "x":
            x_col = col
        else:
            y_col = col
        draw()
    return set_col

left = tk.Frame(root); left.pack(side=tk.LEFT, fill=tk.Y)
bottom = tk.Frame(root); bottom.pack(side=tk.BOTTOM, fill=tk.X)
for c in NUM_COLS:
    tk.Button(left, text=c, command=make_setter("x")).pack(fill=tk.X)
    tk.Button(bottom, text=c, command=make_setter("y")).pack(side=tk.LEFT)

def save():
    h, m, s = time.localtime()[3:6]
    fig.savefig(f"graph{h:02d}_{m:02d}_{s:02d}.png")

tk.Button(left, text="Сохранить", command=save).pack(fill=tk.X)
draw()
root.mainloop()