import os
import threading
import pandas as pd
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.filechooser import FileChooserListView, FileSystemAbstract
from kivy.uix.label import Label


class FolderSelectionDialog(FloatLayout):
    def __init__(self, **kwargs):
        super(FolderSelectionDialog, self).__init__(**kwargs)
        self.file_chooser = FileChooserListView(
            path=os.path.expanduser("~"), filters=["[\\w\\s]+/"]
        )
        self.add_widget(self.file_chooser)

        self.folder_button = Button(text="Select")
        self.folder_button.bind(on_press=self.select_folder)
        self.add_widget(self.folder_button)

    def select_folder(self, instance):
        self.parent.folder_path = self.file_chooser.path
        
        self.parent.dismiss()


class MainApp(App):
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        self.folder_path = ""

    def build(self):

        self.layout = FloatLayout()


        file_dialog = FolderSelectionDialog()
        self.file_dialog_popup = Popup(title="Select Folder", content=file_dialog, size_hint=(0.9, 0.9))

    
        self.combine_dialog = Popup(title="Combine CSV Files", size_hint=(0.7, 0.2))

        self.progress_bar = ProgressBar(max=100)

        
        combine_button = Button(text="Combine CSV Files", disabled=True)
        combine_button.bind(on_press=self.combine_files)

        
        folder_button = Button(text="Select Folder")
        folder_button.bind(on_press=self.open_folder_selection_dialog)
        folder_button.bind(on_release=self.layout.remove_widget(folder_button))

        self.layout.add_widget(combine_button)
        self.layout.add_widget(folder_button)

        return self.layout


        

    def open_folder_selection_dialog(self, instance):
        self.file_dialog_popup.open()
        


    def combine_files(self, instance):
        threading.Thread(target=self.combine_file_thread).start()

    def combine_file_thread(self):
       
        csv_files = [f for f in os.listdir(self.folder_path) if f.endswith(".csv")]
        df_list = []
        total_rows = 0
        total_cols = 0
        for file_name in csv_files:
            file_path = os.path.join(self.folder_path, file_name)
            try:
                df = pd.read_csv(file_path)
                df_list.append(df)
                total_rows += df.shape[0]
                total_cols += df.shape[1]
            except pd.errors.EmptyDataError:
                pass


        combined_df = pd.concat(df_list, axis=0, ignore_index=True)

        output_file_name = "combined_file.csv"
        output_file_path = os.path.join(self.folder_path, output_file_name)
        combined_df.to_csv(output_file_path, index=False)

     
        message = f"Output File: {output_file_name}\nTotal Rows: {total_rows}\nTotal Columns: {total_cols}"
        self.show_output_message(message)

    def show_output_message(self, message):
        output_dialog = Popup(title="Output Message", size_hint=(0.7, 0.3))
        output_layout = FloatLayout()

        output_label = Label(text=message, size_hint=(0.9, 0.9), pos_hint={"x": 0.05, "y": 0.1})
        output_layout.add_widget(output_label)

      
        ok_button = Button(text="OK", size_hint=(0.2, 0.2), pos_hint={"x": 0.4, "y": 0.1})
        ok_button.bind(on_press=output_dialog.dismiss)
        output_layout.add_widget(ok_button)


        output_dialog.content = output_layout
        output_dialog.open()

if __name__ == "__main__":
    MainApp().run()
