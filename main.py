import mysql.connector
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox

# Параметри підключення до бази даних
host = "localhost"
user = "root"
password = "1809"
database = "ecomon"

# Глобальна змінна для збереження ідентифікатора виділеного запису
selected_id = None
selected_item = None

# Функція для імпорту даних з Excel-файлу
def import_data():
    # Відкриття файлового діалогу для вибору файлу Excel
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])

    if not file_path:
        return  # Користувач скасував вибір файлу

    try:
        # Підключення до бази даних
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        cursor = connection.cursor()

        # Завантаження даних з Excel-файлу
        df = pd.read_excel(file_path)

        # Імпорт даних до таблиці "data"
        for index, row in df.iterrows():
            data = (row['year'], row['objectName'], row['activity'], row['location'], row['no2'], row['so2'], row['co'], row['microparts'], row['summary'])
            insert_query = "INSERT INTO data (year, objectName, activity, location, no2, so2, co, microparts, summary) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, data)

        # Збереження змін до бази даних
        connection.commit()

        # Закриття курсора та з'єднання
        cursor.close()
        connection.close()

        messagebox.showinfo("Успіх", "Дані імпортовано успішно.")

        # Оновлення таблиці після імпорту
        display_table()
    except Exception as e:
        messagebox.showerror("Помилка", f"Виникла помилка: {str(e)}")

# Функція для виведення таблиці
def display_table():
    connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
    cursor = connection.cursor()

    # Очищення поточного вмісту таблиці
    for item in table.get_children():
        table.delete(item)

    # Вибір всіх записів з таблиці "data"
    cursor.execute("SELECT * FROM data")
    records = cursor.fetchall()

    # Додавання нових записів до таблиці
    for record in records:
        table.insert("", "end", values=record)

    connection.close()

# Функція для видалення запису
def delete_record():
    global selected_id, selected_item
    selected_items = table.selection()

    if selected_items:
        selected_item = selected_items[0]
        selected_id = table.item(selected_item, "values")[9]  # Отримання ID обраного запису

        confirmation = messagebox.askyesno("Видалити запис", "Ви впевнені, що бажаєте видалити цей запис?")
        if confirmation:
            connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
            cursor = connection.cursor()
            delete_query = "DELETE FROM data WHERE id = %s"
            cursor.execute(delete_query, (selected_id,))
            connection.commit()
            connection.close()
            display_table()
    else:
        messagebox.showwarning("Не обрано запис", "Будь ласка, виберіть запис для видалення.")

# Функція для відкриття вікна редагування запису
def open_edit_record_window():
    global selected_id, selected_item
    if selected_item:
        add_edit_record("Редагування запису", selected_id)

# Функція для додавання або редагування запису
def add_edit_record(title, record_id=None):
    def save_record():
        year = year_entry.get()
        object_name = object_name_entry.get()
        activity = activity_entry.get()
        location = location_entry.get()
        no2 = no2_entry.get()
        so2 = so2_entry.get()
        co = co_entry.get()
        microparts = microparts_entry.get()
        summary = summary_entry.get()

        try:
            connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
            cursor = connection.cursor()

            if record_id is None:  # Додавання нового запису
                insert_query = "INSERT INTO data (year, objectName, activity, location, no2, so2, co, microparts, summary) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                data = (year, object_name, activity, location, no2, so2, co, microparts, summary)
                cursor.execute(insert_query, data)
            else:  # Редагування існуючого запису
                update_query = "UPDATE data SET year = %s, objectName = %s, activity = %s, location = %s, no2 = %s, so2 = %s, co = %s, microparts = %s, summary = %s WHERE id = %s"
                data = (year, object_name, activity, location, no2, so2, co, microparts, summary, record_id)
                cursor.execute(update_query, data)

            connection.commit()
            connection.close()
            display_table()
            add_edit_window.destroy()  # Закрити вікно після додавання або редагування запису
        except Exception as e:
            messagebox.showerror("Помилка", f"Виникла помилка: {str(e)}")

    add_edit_window = tk.Toplevel(root)
    add_edit_window.title(title)

    # Створення полів для введення даних
    year_label = tk.Label(add_edit_window, text="Рік")
    year_label.grid(row=0, column=0)
    year_entry = tk.Entry(add_edit_window)
    year_entry.grid(row=0, column=1)


    object_name_label = tk.Label(add_edit_window, text="Назва об'єкту")
    object_name_label.grid(row=1, column=0)
    object_name_entry = tk.Entry(add_edit_window)
    object_name_entry.grid(row=1, column=1)

    activity_label = tk.Label(add_edit_window, text="Діяльність")
    activity_label.grid(row=2, column=0)
    activity_entry = tk.Entry(add_edit_window)
    activity_entry.grid(row=2, column=1)

    location_label = tk.Label(add_edit_window, text="Місце")
    location_label.grid(row=3, column=0)
    location_entry = tk.Entry(add_edit_window)
    location_entry.grid(row=3, column=1)

    no2_label = tk.Label(add_edit_window, text="NO2")
    no2_label.grid(row=4, column=0)
    no2_entry = tk.Entry(add_edit_window)
    no2_entry.grid(row=4, column=1)

    so2_label = tk.Label(add_edit_window, text="SO2")
    so2_label.grid(row=5, column=0)
    so2_entry = tk.Entry(add_edit_window)
    so2_entry.grid(row=5, column=1)

    co_label = tk.Label(add_edit_window, text="CO")
    co_label.grid(row=6, column=0)
    co_entry = tk.Entry(add_edit_window)
    co_entry.grid(row=6, column=1)

    microparts_label = tk.Label(add_edit_window, text="Мікрочастки")
    microparts_label.grid(row=7, column=0)
    microparts_entry = tk.Entry(add_edit_window)
    microparts_entry.grid(row=7, column=1)

    summary_label = tk.Label(add_edit_window, text="Сума хімічних речовин")
    summary_label.grid(row=8, column=0)
    summary_entry = tk.Entry(add_edit_window)
    summary_entry.grid(row=8, column=1)

    save_button = tk.Button(add_edit_window, text="Зберегти", command=save_record)
    save_button.grid(row=9, columnspan=2)

    selected_id = record_id

    if selected_id is not None:
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM data WHERE id = %s", (selected_id,))
        record = cursor.fetchone()
        connection.close()

        if record:
            year, object_name, activity, location, no2, so2, co, microparts, summary = record[0:9]
            year_entry.insert(0, year)
            object_name_entry.insert(0, object_name)
            activity_entry.insert(0, activity)
            location_entry.insert(0, location)
            no2_entry.insert(0, no2)
            so2_entry.insert(0, so2)
            co_entry.insert(0, co)
            microparts_entry.insert(0, microparts)
            summary_entry.insert(0, summary)

# Функція для виділення запису та збереження ідентифікатора для редагування
def select_record(event):
    global selected_id, selected_item
    selected_items = table.selection()
    if selected_items:
        selected_item = selected_items[0]
        selected_id = table.item(selected_item, "values")[9]

# Створення головного вікна програми
root = tk.Tk()
root.title("Імпорт даних з Excel до MySQL")

root.geometry('1550x400')
root['bg'] ='purple'
# Створення Treeview для відображення таблиці
table = ttk.Treeview(root, columns=("year", "objectName", "activity", "location", "no2", "so2", "co", "microparts", "summary"))
table.heading("#1", text="Рік", anchor="w")
table.heading("#2", text="Назва об'єкту", anchor="w")
table.heading("#3", text="Діяльність", anchor="w")
table.heading("#4", text="Місце", anchor="w")
table.heading("#5", text="NO2", anchor="w")
table.heading("#6", text="SO2", anchor="w")
table.heading("#7", text="CO", anchor="w")
table.heading("#8", text="Мікрочастки", anchor="w")
table.heading("#9", text="Сума хімічних речовин", anchor="w")
table.column("#0", width=0)
table.column("#1", width=40)
table.column("#2", width=310)
table.column("#3", width=500)
table.column("#4", width=100)
table.column("#5", width=100)
table.column("#6", width=100)
table.column("#7", width=100)
table.column("#8", width=100)
table.column("#9", width=200)
# Підключіть функцію для виділення запису
table.bind("<ButtonRelease-1>", select_record)
table.grid(row=0, column=0, columnspan=4)

import_button = tk.Button(root, text="Імпортувати дані з Excel", command=import_data)
import_button.grid(row=1, column=0)
add_button = tk.Button(root, text="Додати запис", command=lambda: add_edit_record("Додати запис"))
add_button.grid(row=1, column=1)
edit_button = tk.Button(root, text="Редагувати запис", command=open_edit_record_window)
edit_button.grid(row=1, column=2)
delete_button = tk.Button(root, text="Видалити запис", command=delete_record)
delete_button.grid(row=1, column=3)

display_table()

# Запуск головного циклу tkinter
root.mainloop()

