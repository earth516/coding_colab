import tkinter as tk
from tkinter import ttk
import requests
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def fetch_data_for_date(date):
    try:
        url = f'http://www.khoa.go.kr/api/oceangrid/tideObsTemp/search.do?ServiceKey=VkKixcDPfAWm7PV5tBnoSA==&ObsCode=DT_0005&Date={date}&ResultType=json'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return {}

def plot_data(start_date, end_date, filter_time):
    filtered_records = []
    
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y%m%d')
        data = fetch_data_for_date(date_str)
        
        if not data or 'result' not in data or 'data' not in data['result']:
            current_date += timedelta(days=1)
            continue
        
        records = data['result']['data']

        for record in records:
            record_time = record.get('record_time', '')
            if record_time:
                try:
                    record_datetime = datetime.strptime(record_time, '%Y-%m-%d %H:%M:%S')
                    if record_datetime.strftime('%H:%M:%S') == filter_time:
                        filtered_records.append(record)
                except ValueError:
                    continue

        current_date += timedelta(days=1)

    if filtered_records:
        df = pd.DataFrame(filtered_records)
        df['record_time'] = pd.to_datetime(df['record_time'])
        df['water_temp'] = pd.to_numeric(df['water_temp'], errors='coerce')
        df = df.dropna(subset=['water_temp'])
        df = df.drop_duplicates()
        df.set_index('record_time', inplace=True)
        
        plt.figure(figsize=(10, 6))
        plt.plot(df.index, df['water_temp'], marker='o', linestyle='-', color='b')
        plt.title(f'Water Temperature from {start_date} to {end_date} at {filter_time}')
        plt.xlabel('Date')
        plt.ylabel('Water Temperature (°C)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        return plt.gcf()
    else:
        print("No records found.")
        return None

def on_plot_button_click():
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    filter_time = filter_time_entry.get()
    
    print(f"Fetching data from {start_date} to {end_date} at {filter_time}.")
    
    fig = plot_data(start_date, end_date, filter_time)
    if fig:
        print("Figure created successfully.")
        for widget in plot_frame.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    else:
        print("No data available or figure creation failed.")

root = tk.Tk()
root.title("Water Temperature Plotter")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

tk.Label(frame, text="Start Date (YYYY-MM-DD)").grid(row=0, column=0, padx=5, pady=5)
start_date_entry = tk.Entry(frame)
start_date_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="End Date (YYYY-MM-DD)").grid(row=1, column=0, padx=5, pady=5)
end_date_entry = tk.Entry(frame)
end_date_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame, text="Filter Time (HH:MM:SS)").grid(row=2, column=0, padx=5, pady=5)
filter_time_entry = tk.Entry(frame)
filter_time_entry.grid(row=2, column=1, padx=5, pady=5)

plot_button = tk.Button(frame, text="Plot Data", command=on_plot_button_click)
plot_button.grid(row=3, columnspan=2, pady=10)

plot_frame = tk.Frame(root)
plot_frame.pack(fill=tk.BOTH, expand=True)

root.mainloop()
