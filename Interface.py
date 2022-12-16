import tkinter as tk
from tkinter import ttk

order_by_rating_flag = True


def open_gui(data):
    root = tk.Tk()
    root.title('Movies')
    root.geometry('800x305')
    # define columns
    columns = ('Title', 'Genre', 'Directors', 'Rating')

    tree = ttk.Treeview(root, columns=columns, show='headings')

    # define headings
    tree.heading('Title', text='Title')
    tree.heading('Genre', text='Genre')
    tree.heading('Directors', text='Directors')
    tree.heading('Rating', text='Rating')

    def sort_by_genre():
        sorted_list = sorted(data, key=lambda x: x[1])
        x = tree.get_children()
        for values, child in zip(sorted_list, x):
            tree.item(child, values=values)

    def sort_by_title():
        sorted_list = sorted(data, key=lambda x: x[0])
        x = tree.get_children()
        for values, child in zip(sorted_list, x):
            tree.item(child, values=values)

    def order_by_rating():
        global order_by_rating_flag
        if order_by_rating_flag:
            sorted_list = sorted(data, key=lambda x: x[3])
            x = tree.get_children()
            for values, child in zip(sorted_list, x):
                tree.item(child, values=values)
            order_by_rating_flag = not order_by_rating_flag
        else:
            sorted_list = sorted(data, key=lambda x: x[3], reverse=True)
            x = tree.get_children()
            for values, child in zip(sorted_list, x):
                tree.item(child, values=values)
            order_by_rating_flag = not order_by_rating_flag

    for contact in data:
        print(contact)
        tree.insert('', tk.END, values=contact)

    tree.grid(row=0, column=0, sticky='nsew')

    # add a scrollbar
    scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='ns')

    # add the buttons
    button_by_rating = ttk.Button(root, command=order_by_rating, text='sort by rating')
    button_by_rating.grid()
    button_by_title = ttk.Button(root, command=sort_by_title, text='sort by title')
    button_by_title.grid()
    button_by_genres = ttk.Button(root, command=sort_by_genre, text='sort by genre')
    button_by_genres.grid()
    # run the app
    root.mainloop()
