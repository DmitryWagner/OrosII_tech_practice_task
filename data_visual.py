import tkinter as tk
from tkinter import ttk
import time
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import colormaps  # Современный способ импорта цветовых схем
import dataset

# --- ИНДИВИДУАЛЬНЫЕ НАСТРОЙКИ ---
MARKER = "*"  # ID 70216990 -> сумма 7 -> звезда
DEFAULT_CMAP = "PuRd"  # Фамилия Орос -> схема PuRd

# --- СПИСКИ КОЛОНОК ---
# Берем списки из dataset.py
NUM_COLS = dataset.NUMERIC_COLS
CAT_COLS = dataset.CATEGORICAL_COLS
ALL_COLS = NUM_COLS + CAT_COLS

# Текущие выбранные колонки
x_col = NUM_COLS[0]
y_col = NUM_COLS[1]
current_cmap = DEFAULT_CMAP

# --- НАСТРОЙКА ОКНА ---
root = tk.Tk()
root.title("Улучшенная визуализация")
root.geometry("1300x800")

# --- ХОЛСТ ДЛЯ ГРАФИКА ---
fig = Figure(figsize=(8, 6))
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)


# --- ФУНКЦИЯ ОТРИСОВКИ ---
def draw():
    ax.clear()
    df = dataset.df

    x_is_num = x_col in NUM_COLS
    y_is_num = y_col in NUM_COLS
    x_is_cat = x_col in CAT_COLS
    y_is_cat = y_col in CAT_COLS

    # 1. Одна и та же числовая колонка -> ГИСТОГРАММА
    if x_col == y_col and x_is_num:
        data = df[x_col].dropna()
        counts, bins, patches = ax.hist(data, bins=10, edgecolor='white')

        cmap = colormaps[current_cmap]
        for i, patch in enumerate(patches):
            patch.set_facecolor(cmap(i / len(patches)))

        ax.set_xlabel(x_col)
        ax.set_ylabel("Частота")
        # Подписи над столбцами
        for count, bin_ in zip(counts, bins):
            ax.text(bin_ + (bins[1] - bins[0]) / 2, count, str(int(count)), ha='center', va='bottom')

    # 2. Одна и та же категориальная колонка -> КРУГОВАЯ
    elif x_col == y_col and x_is_cat:
        counts = df[x_col].value_counts()
        cmap = colormaps[current_cmap]
        colors = [cmap(i / len(counts)) for i in range(len(counts))]

        # Ограничиваем количество секторов, чтобы не зависло на датах
        if len(counts) > 15:
            counts = counts.head(15)
            colors = colors[:15]

        ax.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.set_ylabel(x_col)

    # 3. Ось X - категориальная -> СТОЛБЧАТАЯ
    elif x_is_cat:
        counts = df[x_col].value_counts()
        # Ограничиваем количество столбцов для читаемости
        if len(counts) > 20:
            counts = counts.head(20)

        cmap = colormaps[current_cmap]
        colors = [cmap(i / len(counts)) for i in range(len(counts))]

        ax.bar(counts.index.astype(str), counts.values, color=colors)
        ax.set_xlabel(x_col)
        ax.set_ylabel("Количество записей (N)")

        # Поворачиваем подписи, если их много
        if len(counts) > 5:
            ax.tick_params(axis='x', rotation=45)

    # 4. Ось X - числовая, Y - категориальная -> КОРОБОЧНАЯ
    elif y_is_cat and x_is_num:
        df.boxplot(column=x_col, by=y_col, ax=ax, grid=False)
        ax.set_xlabel(y_col)
        ax.set_ylabel(x_col)
        fig.suptitle("")  # Убираем автоматический заголовок pandas

    # 5. Иначе (числовая на числовую) -> ТОЧЕЧНАЯ
    else:
        ax.scatter(df[x_col], df[y_col], marker=MARKER, alpha=0.6)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)

    canvas.draw()


# --- ОБРАБОТЧИКИ ---
def set_x(col):
    global x_col
    x_col = col
    draw()


def set_y(col):
    global y_col
    y_col = col
    draw()


def change_cmap(event):
    global current_cmap
    current_cmap = cmap_combo.get()
    draw()


def save():
    h, m, s = time.localtime()[3:6]
    filename = f"graph{h:02d}_{m:02d}_{s:02d}.png"
    fig.savefig(filename)
    print(f"График сохранен в {filename}")


# --- ИНТЕРФЕЙС ---

# Верхняя панель с выпадающим списком (29 схем)
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

tk.Label(top_frame, text="Цветовая схема (cmap):").pack(side=tk.LEFT)

cmaps_list = [
    'viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Greys', 'Purples', 'Blues',
    'Greens', 'Oranges', 'Reds', 'YlOrBr', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu',
    'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 'binary', 'gist_yarg', 'spring', 'summer',
    'autumn', 'winter', 'cool', 'hot'
]

cmap_combo = ttk.Combobox(top_frame, values=cmaps_list, state="readonly", width=20)
cmap_combo.set(DEFAULT_CMAP)
cmap_combo.pack(side=tk.LEFT, padx=10)
cmap_combo.bind("<<ComboboxSelected>>", change_cmap)

# Левая панель кнопок (Ось X)
left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
tk.Label(left_frame, text="Ось X:").pack(pady=5)

for col_name in ALL_COLS:
    tk.Button(left_frame, text=col_name, command=lambda c=col_name: set_x(c)).pack(fill=tk.X, pady=2)

# Нижняя панель кнопок (Ось Y)
bottom_frame = tk.Frame(root)
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
tk.Label(bottom_frame, text="Ось Y:").pack(side=tk.LEFT, padx=5)

for col_name in ALL_COLS:
    tk.Button(bottom_frame, text=col_name, command=lambda c=col_name: set_y(c)).pack(side=tk.LEFT, padx=2)

# Кнопка сохранения
tk.Button(bottom_frame, text="Сохранить", command=save, bg="#15455A", fg="white", font=("Arial", 10, "bold")).pack(
    side=tk.RIGHT, padx=15)

# Первичная отрисовка и запуск
draw()
root.mainloop()