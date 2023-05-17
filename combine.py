import tkinter as tk
from tkinter import *
from tkinter import filedialog
import os
import threading
import pandas as pd

window = tk.Tk()
window.title("CSV File Combine Tool")
 

window.geometry("700x500")
 
textVar = StringVar()
textVar.set('Select a folder')


label = tk.Label(window, textvariable=textVar,
font=('Calibri 15 bold'))
label.pack(pady=20)


def on_click_btn1():
    global folder_selected
    folder_selected  = filedialog.askdirectory()
    folder_content = (os.listdir(folder_selected))

    textVar.set('You have selected the below folder path: \n' + folder_selected + "\n " + sanitize_folder_contents(folder_content))
    
def sanitize_folder_contents(initial_obj):
    filtered_obj  = list(filter(lambda x: x.lower().endswith('.csv'), initial_obj))
    filtered_obj_str = "\n".join(filtered_obj)
    if len(filtered_obj) == 0:
        btn2.config(state='disabled')
        return 'no CSV files detected inside the selected folder'
    else:
        btn2.config(state='active')
        return "Contents: \n" + filtered_obj_str


def on_click_btn2():
    textVar.set('Loading ...')
    combine_csv_files()
     

btn1 = tk.Button(window, text="Choose a folder", command=on_click_btn1)
btn1.pack(pady=20)
 

btn2 = tk.Button(window, text="Combine CSV files", command=on_click_btn2)
btn2.pack(pady=40)
btn2.config(state='disabled')




def combine_csv_files():

    my_path = folder_selected
    csv_files = [f for f in os.listdir(my_path) if f.endswith(".csv")]
    df_list = []
    total_rows = 0
    total_cols = 0
    threads = []

    for file_name in csv_files:
        file_path = os.path.join(my_path, file_name)
        t = threading.Thread(target=lambda path: read_csv_file(path, df_list, total_rows, total_cols), args=(file_path,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    combined_df = pd.concat(df_list, axis=0, ignore_index=True)


    output_file_name = "combined_file.csv"
    output_file_path = os.path.join(my_path, output_file_name)
    combined_df.to_csv(output_file_path, index=False)

    total_rows, total_cols = combined_df.shape

    message = f"Output File: {output_file_name}\nTotal Rows: {total_rows}\nTotal Columns: {total_cols}"
    textVar.set(message)

def read_csv_file(file_path, df_list, total_rows, total_cols):
    try:
        df = pd.read_csv(file_path)
        df_list.append(df)
        total_rows += df.shape[0]
        total_cols += df.shape[1]
    except pd.errors.EmptyDataError:
        pass

 
window.mainloop()