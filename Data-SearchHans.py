import os
import csv
import shutil
import tkinter as tk
from tkinter import filedialog, ttk

class CustomExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("Data SeachHans v0.0.1")
        self.root.geometry("1200x800")

        self.selected_folder = ""
        self.table_columns = ["DataName"] + ["_{}".format(i) for i in range(1, 21)]
        self.column_widths = {"DataName": 200, "_1": 100, "_2": 100, "_3": 100}  # Adjust column widths as needed

        # First Row (Button Row)
        self.button_row = tk.Frame(root)
        self.button_row.pack(side=tk.TOP, fill=tk.X)

        self.select_folder_button = tk.Button(self.button_row, text="Select Folder", command=self.select_folder)
        self.select_folder_button.pack(side=tk.LEFT, padx=10)

        self.selected_path_label = tk.Label(self.button_row, text="")
        self.selected_path_label.pack(side=tk.LEFT)

        self.export_csv_button = tk.Button(self.button_row, text="Export to CSV", command=self.export_to_csv)
        self.export_csv_button.pack(side=tk.RIGHT, padx=10)

        self.copy_to_path_button = tk.Button(self.button_row, text="Copy to Path", command=self.copy_to_path)
        self.copy_to_path_button.pack(side=tk.RIGHT)

        self.filter_entry = tk.Entry(self.button_row, justify="left", width=30)
        self.filter_entry.pack(side=tk.RIGHT, padx=(20, 10), fill=tk.X)
        
        self.filter_entry_label = tk.Label(self.button_row, text="Search")
        self.filter_entry_label.pack(side=tk.RIGHT)

        # Second Row (Table Row)
        self.table_frame = tk.Frame(root)
        self.table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.table = ttk.Treeview(self.table_frame, columns=self.table_columns, show="headings", height=20)
        for column in self.table_columns:
            self.table.heading(column, text=column, command=lambda c=column: self.sort_column(c, False))
            self.table.column(column, width=self.column_widths.get(column, 100), anchor="center")
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        table_scroll_y = tk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.table.yview)
        table_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.configure(yscrollcommand=table_scroll_y.set)

        # Third Row (Status Bar Row)
        self.status_bar_frame = tk.Frame(root)
        self.status_bar_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.status_bar_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.update_selected_path()
        self.update_table()

        # Bind entry to update table in real-time
        self.filter_entry.bind("<KeyRelease>", self.update_table)

    def select_folder(self):
        self.selected_folder = filedialog.askdirectory()
        self.update_selected_path()
        self.update_table()

    def update_selected_path(self):
        self.selected_path_label.config(text=f"{self.selected_folder}")

    def update_table(self, event=None):
        filter_text = self.filter_entry.get().lower()
        self.table.delete(*self.table.get_children())
        if os.path.isdir(self.selected_folder):
            for folder_name in os.listdir(self.selected_folder):
                folder_path = os.path.join(self.selected_folder, folder_name)
                if os.path.isdir(folder_path) and all(term.lower() in folder_name.lower() for term in filter_text.split(" ")):
                    folder_data = [folder_name] + folder_name.split("_")
                    self.table.insert("", "end", values=folder_data)

    def sort_column(self, col, reverse):
        data = [(self.table.set(child, col), child) for child in self.table.get_children("")]
        try:
            data.sort(key=lambda x: int(x[0]), reverse=reverse)
        except ValueError:
            data.sort(reverse=reverse)
        for i, item in enumerate(data):
            self.table.move(item[1], "", i)
        self.table.heading(col, command=lambda: self.sort_column(col, not reverse))

    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            with open(file_path, "w", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(self.table_columns)
                for child in self.table.get_children():
                    values = self.table.item(child)["values"]
                    csv_writer.writerow(values)
            self.status_var.set("CSV exported successfully.")

    def copy_to_path(self):
        destination_path = filedialog.askdirectory()
        if os.path.isdir(destination_path):
            for child in self.table.selection():
                folder_name = self.table.item(child)["values"][0]
                source_path = os.path.join(self.selected_folder, folder_name)
                destination_folder = os.path.join(destination_path, folder_name)
                shutil.copytree(source_path, destination_folder)
            self.status_var.set("Folders copied successfully.")
        else:
            self.status_var.set("Invalid destination path.")


if __name__ == "__main__":
    root = tk.Tk()
    app = CustomExplorer(root)
    root.mainloop()
