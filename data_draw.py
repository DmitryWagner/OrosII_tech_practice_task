import tkinter as tk
from tkinter import ttk, colorchooser
import time
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import colormaps
import dataset
from PIL import ImageGrab

# --- ИНДИВИДУАЛЬНЫЕ НАСТРОЙКИ ---
MARKER = "*"
DEFAULT_CMAP = "PuRd"
DRAW_THICKNESS = 8  # 7//2 + 5 = 8
DRAW_COLOR = "#15455A"  # RGB(21, 69, 90)

NUM_COLS = dataset.NUMERIC_COLS
CAT_COLS = dataset.CATEGORICAL_COLS
ALL_COLS = NUM_COLS + CAT_COLS

x_col = NUM_COLS[0]
y_col = NUM_COLS[1]
current_cmap = DEFAULT_CMAP

# --- НАСТРОЙКА ОКНА ---
root = tk.Tk()
root.title("Модификация визуализаций")
root.geometry("1400x900")

# --- ХОЛСТ ДЛЯ ГРАФИКА ---
fig = Figure(figsize=(8, 6))
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
canvas_widget = canvas.get_tk_widget()


# --- ФУНКЦИЯ ОТРИСОВКИ ---
def draw():
    ax.clear()
    df = dataset.df

    x_is_num = x_col in NUM_COLS
    x_is_cat = x_col in CAT_COLS
    y_is_cat = y_col in CAT_COLS

    if x_col == y_col and x_is_num:
        data = df[x_col].dropna()
        counts, bins, patches = ax.hist(data, bins=10, edgecolor='white')
        cmap = colormaps[current_cmap]
        for i, patch in enumerate(patches):
            patch.set_facecolor(cmap(i / len(patches)))
        ax.set_xlabel(x_col)
        ax.set_ylabel("Частота")
        for count, bin_ in zip(counts, bins):
            ax.text(bin_ + (bins[1] - bins[0]) / 2, count, str(int(count)), ha='center', va='bottom')

    elif x_col == y_col and x_is_cat:
        counts = df[x_col].value_counts()
        cmap = colormaps[current_cmap]
        colors = [cmap(i / len(counts)) for i in range(len(counts))]
        if len(counts) > 15:
            counts = counts.head(15)
            colors = colors[:15]
        ax.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=colors, startangle=90)

    elif x_is_cat:
        counts = df[x_col].value_counts()
        if len(counts) > 20:
            counts = counts.head(20)
        cmap = colormaps[current_cmap]
        colors = [cmap(i / len(counts)) for i in range(len(counts))]
        ax.bar(counts.index.astype(str), counts.values, color=colors)
        ax.set_xlabel(x_col)
        ax.set_ylabel("Количество записей (N)")
        if len(counts) > 5:
            ax.tick_params(axis='x', rotation=45)

    elif y_is_cat and x_is_num:
        df.boxplot(column=x_col, by=y_col, ax=ax, grid=False)
        ax.set_xlabel(y_col)
        ax.set_ylabel(x_col)
        fig.suptitle("")

    else:
        ax.scatter(df[x_col], df[y_col], marker=MARKER, alpha=0.6)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)

    canvas.draw()


# ==========================================
# ЛОГИКА РИСОВАНИЯ
# ==========================================
drawing_mode = False
strokes = []
current_stroke = None


def toggle_draw():
    global drawing_mode
    drawing_mode = not drawing_mode
    if drawing_mode:
        btn_draw.config(relief=tk.SUNKEN)
        canvas_widget.config(cursor="pencil")
    else:
        btn_draw.config(relief=tk.RAISED)
        canvas_widget.config(cursor="")


def on_press(e):
    global current_stroke
    if not drawing_mode:
        return
    if e.num == 3:  # Если нажата правая кнопка мыши
        toggle_draw()
        return
    current_stroke = []
    paint(e)


def paint(e):
    if not drawing_mode or current_stroke is None:
        return
    t = thickness_var.get()
    try:
        t = int(t)
    except ValueError:
        t = 8

    # Рисуем квадратик
    item = canvas_widget.create_rectangle(
        e.x - t / 2, e.y - t / 2, e.x + t / 2, e.y + t / 2,
        fill=current_color, outline=current_color
    )
    current_stroke.append(item)


def on_release(e):
    global current_stroke
    if current_stroke:
        strokes.append(current_stroke)
        current_stroke = None


def undo(e):
    if current_stroke is not None:
        return
    if strokes:
        for item in strokes.pop():
            canvas_widget.delete(item)


def choose_color():
    global current_color
    color_code = colorchooser.askcolor(title="Выбор цвета", color=current_color)[1]
    if color_code:
        current_color = color_code
        btn_color.config(bg=current_color)


def disable_draw_mode():
    global drawing_mode
    if drawing_mode:
        toggle_draw()


# Обработчики колонок
def set_x(col):
    global x_col
    x_col = col
    disable_draw_mode()
    draw()


def set_y(col):
    global y_col
    y_col = col
    disable_draw_mode()
    draw()


def change_cmap(event):
    global current_cmap
    current_cmap = cmap_combo.get()
    draw()


def save():
    h, m, s = time.localtime()[3:6]
    filename = f"graph{h:02d}_{m:02d}_{s:02d}.png"

    # Делаем скриншот области холста, чтобы захватить нарисованное
    root.update()
    x = canvas_widget.winfo_rootx()
    y = canvas_widget.winfo_rooty()
    w = canvas_widget.winfo_width()
    hgt = canvas_widget.winfo_height()

    ImageGrab.grab(bbox=(x, y, x + w, y + hgt)).save(filename)
    print(f"Сохранено: {filename}")


# ==========================================
# ИНТЕРФЕЙС
# ==========================================

# Верхняя панель
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

tk.Label(top_frame, text="cmap:").pack(side=tk.LEFT)
cmaps_list = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Greys', 'Purples', 'Blues',
              'Greens', 'Oranges', 'Reds', 'YlOrBr', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu',
              'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 'binary', 'gist_yarg', 'spring', 'summer',
              'autumn', 'winter', 'cool', 'hot']
cmap_combo = ttk.Combobox(top_frame, values=cmaps_list, state="readonly", width=15)
cmap_combo.set(DEFAULT_CMAP)
cmap_combo.pack(side=tk.LEFT, padx=10)
cmap_combo.bind("<<ComboboxSelected>>", change_cmap)

# Панель рисования
tk.Label(top_frame, text="|").pack(side=tk.LEFT, padx=5)
btn_draw = tk.Button(top_frame, text="Рисование", command=toggle_draw, width=12)
btn_draw.pack(side=tk.LEFT, padx=5)

tk.Label(top_frame, text="Толщина:").pack(side=tk.LEFT)
thickness_var = tk.IntVar(value=DRAW_THICKNESS)
tk.Spinbox(top_frame, from_=1, to=50, textvariable=thickness_var, width=5).pack(side=tk.LEFT, padx=5)

tk.Label(top_frame, text="Цвет:").pack(side=tk.LEFT)
current_color = DRAW_COLOR
btn_color = tk.Button(top_frame, bg=current_color, width=3, command=choose_color)
btn_color.pack(side=tk.LEFT, padx=5)

# Левая панель (X)
left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
tk.Label(left_frame, text="Ось X:").pack()
for col_name in ALL_COLS:
    tk.Button(left_frame, text=col_name, command=lambda c=col_name: set_x(c)).pack(fill=tk.X, pady=2)

# Нижняя панель (Y)
bottom_frame = tk.Frame(root)
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
tk.Label(bottom_frame, text="Ось Y:").pack(side=tk.LEFT)
for col_name in ALL_COLS:
    tk.Button(bottom_frame, text=col_name, command=lambda c=col_name: set_y(c)).pack(side=tk.LEFT, padx=2)

tk.Button(bottom_frame, text="Сохранить", command=save, bg="#15455A", fg="white", font=("Arial", 10, "bold")).pack(
    side=tk.RIGHT, padx=15)

# --- ПРИВЯЗКА СОБЫТИЙ МЫШИ И КЛАВИАТУРЫ ---
canvas_widget.bind("<Button-1>", on_press)
canvas_widget.bind("<B1-Motion>", paint)
canvas_widget.bind("<ButtonRelease-1>", on_release)
canvas_widget.bind("<Button-3>", on_press)  # Правая кнопка мыши
root.bind("<Control-z>", undo)

# Первичная отрисовка и запуск
draw()
root.mainloop()