import os
import csv
import shutil
import tkinter as tk
from tkinter import filedialog, ttk
import subprocess
from xml.etree import ElementTree as ET

class CustomExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("Data SeachHans v0.0.1")
        self.root.geometry("1320x800")

        self.selected_folder = ""
        self.table_columns = ["DataName", "Source", "DateTime", "RequestNo", "SceneNo", "Direction", "Swath", "Mode", "P.Type1", "P.Type2", "Level", "Lat", "Lon"]  # Modified column names
        self.column_widths = {"DataName": 380, "Source": 60, "DateTime": 120, "Direction": 60, "Mode": 60, "Level": 60, "P.Type1": 60, "P.Type2": 60, "Lat": 100, "Lon": 100}  # Adjust column widths as needed

        # First Row (Button Row)
        self.button_row = tk.Frame(root)
        self.button_row.pack(side=tk.TOP, fill=tk.X, padx=(0, 10))

        self.select_folder_button = tk.Button(self.button_row, text="폴더 선택", command=self.select_folder)
        self.select_folder_button.pack(side=tk.LEFT, padx=10)

        self.export_csv_button = tk.Button(self.button_row, text="CSV 내보내기", command=self.export_to_csv)
        self.export_csv_button.pack(side=tk.LEFT, padx=10)

        self.copy_to_path_button = tk.Button(self.button_row, text="폴더 복사", command=self.copy_to_path)
        self.copy_to_path_button.pack(side=tk.LEFT, padx=10)

        self.filter_entry_label = tk.Label(self.button_row, justify="right", text="▶검색(띄워쓰기 AND 조건) :")
        self.filter_entry_label.pack(side=tk.LEFT, padx=5)

        self.filter_entry = tk.Entry(self.button_row, justify="left", width=30)
        self.filter_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X)

        # Bind button to update table
        self.update_table_button = tk.Button(self.button_row, text="검색", command=self.update_table)
        self.update_table_button.pack(side=tk.LEFT, padx=5)

        self.filter_cancel_button = tk.Button(self.button_row, text="초기화", command=self.cancel_filter)
        self.filter_cancel_button.pack(side=tk.LEFT, padx=2)

        # Second Row (Table Row)
        self.table_frame = tk.Frame(root)
        self.table_frame.pack(side=tk.TOP, fill=tk.BOTH, padx=(10, 10), expand=True)

        self.table = ttk.Treeview(self.table_frame, columns=self.table_columns, show="headings", height=20)
        for column in self.table_columns:
            self.table.heading(column, text=column, command=lambda c=column: self.sort_column(c, False))
            self.table.column(column, width=self.column_widths.get(column, 75), anchor="center")
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        table_scroll_y = tk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.table.yview)
        table_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.configure(yscrollcommand=table_scroll_y.set)

        # Double click event handler for table items
        self.table.bind("<Double-1>", self.double_click_handler)

        # Third Row (Status Bar Row)
        self.status_bar_frame = tk.Frame(root)
        self.status_bar_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.status_bar_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # "L1C 데이터에서 위치 가져오기" 버튼
        self.get_coordinates_button = tk.Button(self.status_bar_frame, text="동일 L1C 데이터에서 위치불러오기", command=self.get_coordinates)
        self.get_coordinates_button.pack(side=tk.BOTTOM, padx=10, pady=5)

        self.update_selected_path()

    def select_folder(self):
        self.selected_folder = filedialog.askdirectory()
        self.update_selected_path()
        self.update_table()  # Update table immediately after selecting folder

    def update_selected_path(self):
        num_folders = 0
        if os.path.isdir(self.selected_folder):
            num_folders = len([name for name in os.listdir(self.selected_folder) if os.path.isdir(os.path.join(self.selected_folder, name))])
        self.root.title(f"Data SeachHans v0.0.1 - {self.selected_folder} ({num_folders} datasets)")  # Update window title with selected folder and number of datasets

    def update_table(self):
        filter_text = self.filter_entry.get().lower()
        self.table.delete(*self.table.get_children())
        if os.path.isdir(self.selected_folder):
            for folder_name in os.listdir(self.selected_folder):
                folder_path = os.path.join(self.selected_folder, folder_name)
                if os.path.isdir(folder_path) and all(term.lower() in folder_name.lower() for term in filter_text.split(" ")):
                    folder_data = [folder_name] + folder_name.split("_")[:10]  # Modify folder_data
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

    def cancel_filter(self):
        self.filter_entry.delete(0, tk.END)
        self.update_table()

    def double_click_handler(self, event):
        selected_item = self.table.selection()[0]
        folder_name = self.table.item(selected_item, "values")[0]
        click_path = os.path.join(self.selected_folder, folder_name).replace('/', '\\')  # Replace forward slashes with backward slashes
        print(click_path)
        subprocess.Popen(f'explorer "{click_path}"')  # Open folder in file explorer

    def export_to_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            with open(filename, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(self.table_columns)
                for item in self.table.get_children():
                    writer.writerow([self.table.item(item, "values")[i] for i in range(len(self.table_columns))])

    def copy_to_path(self):
        destination_folder = filedialog.askdirectory()
        if destination_folder:
            for item in self.table.selection():
                folder_name = self.table.item(item, "values")[0]
                source_path = os.path.join(self.selected_folder, folder_name)
                shutil.copytree(source_path, os.path.join(destination_folder, folder_name))

    def get_coordinates(self):
        for child in self.table.get_children():
            folder_name = self.table.item(child)["values"][0]
            folder_path = os.path.join(self.selected_folder, folder_name)
            if len(folder_name) >= 50 and folder_name[49] == 'C':  # Validate folder name
                kml_file = self.find_kml_file(folder_path)
                if kml_file:
                    Lat, Lon = self.get_kml_center(kml_file)
                    self.table.set(child, "Lat", Lat)
                    self.table.set(child, "Lon", Lon)

    def find_kml_file(self, folder_path):
        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith('.kml'):
                return os.path.join(folder_path, file_name)
        return None

    def get_kml_center(self, kml_file):
        tree = ET.parse(kml_file)
        root = tree.getroot()

        # Find Polygon coordinates from gx:LatLonQuad
        coordinates_str = root.find(".//{http://www.opengis.net/kml/2.2}coordinates").text.strip()
        coordinates_list = [coord.strip().split(",") for coord in coordinates_str.split()]

        # Calculate polygon center coordinates
        if coordinates_list:
            Lats = [float(coord[1]) for coord in coordinates_list]
            Lons = [float(coord[0]) for coord in coordinates_list]
            center_Lat = sum(Lats) / len(Lats)
            center_Lon = sum(Lons) / len(Lons)
            return center_Lat, center_Lon
        else:
            return None, None

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomExplorer(root)
    root.mainloop()
