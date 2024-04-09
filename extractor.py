import babel
from babel import numbers
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import re
from tkcalendar import DateEntry
import os

# Function to extract numbers after render time
def extract_numbers_after_render_time(string):
    matches = re.findall(r'render time[^0-9]*([0-9]*\.?[0-9]+)', string, re.IGNORECASE)
    total_seconds = sum(float(match) for match in matches)
    return total_seconds

# Function to format time
def format_time(seconds):
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    seconds = int(seconds % 60)
    return hours, minutes, seconds

# Function to browse for a file and select a period for calculation
def browse_file():
    global selected_file_path  # Declare global variable to store selected file path
    selected_file_path = filedialog.askopenfilename()  # Get the selected file path
    if selected_file_path:
        selected_file_label.config(text="Selected file: " + os.path.basename(selected_file_path))  # Update label with file name

# Function to extract data from the selected file
def extract_data():
    global selected_file_path
    if not selected_file_path:
        result_label.config(text="Select list")
        selected_file_label.config(text="No file selected")  # Show "No file selected" only if no file is selected
    else:
        if os.path.exists(selected_file_path):  # Check if the selected path points to a valid file or directory
            if os.access(selected_file_path, os.R_OK):  # Check if the file is readable
                start_datetime = start_date.get_date().strftime("%Y-%m-%d") + " " + start_time.get()
                end_datetime = end_date.get_date().strftime("%Y-%m-%d") + " " + end_time.get()
                
                try:
                    with open(selected_file_path, 'r') as file:
                        total_seconds = 0
                        for line in file:
                            try:
                                if start_datetime <= line.split()[0] <= end_datetime:
                                    total_seconds += extract_numbers_after_render_time(line)
                            except IndexError:
                                pass
                        
                        if total_seconds > 0:
                            result_label.config(text=f"Total render time: {total_seconds} seconds")
                            hours, minutes, seconds = format_time(total_seconds)
                            result_label.config(text=result_label.cget("text") + f" ({hours} hours, {minutes} minutes, {seconds} seconds)")
                            copy_button.place(relx=0.85, rely=0.9, anchor="center")  # Position the copy button closer to the right
                        else:
                            result_label.config(text="No data found for the selected period")
                except Exception as e:
                    result_label.config(text=f"Error: {str(e)}")
            else:
                result_label.config(text="Permission denied: Cannot read the file")
        else:
            result_label.config(text="File path does not exist")

# Function to copy total seconds to clipboard
def copy_total_seconds():
    match = re.search(r"Total render time: (\d+\.?\d*) seconds", result_label.cget("text"))
    if match:
        total_seconds = match.group(1)
        window.clipboard_clear()
        window.clipboard_append(total_seconds)
        messagebox.showinfo("Copied", f"Total seconds ({total_seconds}) copied to clipboard.")
    else:
        messagebox.showerror("Error", "No total render time found.")

# Function to load image from URL
def load_image_from_url(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return ImageTk.PhotoImage(img)

# Create a Tkinter window
window = tk.Tk()
window.title("Render Time Calculator")
window.configure(bg="#111111")  # Set dark background color

# Load image from URL (replace URL_OF_YOUR_IMAGE with the actual URL)
image_url = "https://media.licdn.com/dms/image/D4D12AQFmA3W_IZbzOw/article-cover_image-shrink_600_2000/0/1684376857233?e=2147483647&v=beta&t=gNU6v2J6EBFG6GaEjCKUdyxD1NLiQ0IokgsuVAHY9ZQ"
logo_image = load_image_from_url(image_url)

# Get the dimensions of the image
image_width = logo_image.width()
image_height = logo_image.height()

# Set window size to match image dimensions
window.geometry(f"{image_width}x{image_height}")

# Create a label to display the background logo
background_label = tk.Label(window, image=logo_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Create DateEntry widgets for selecting start and end dates with red background
start_date = DateEntry(window, width=12, background='#b50808', foreground='white', borderwidth=2)
start_date.place(relx=0.25, rely=0.6, anchor="center")

end_date = DateEntry(window, width=12, background='#b50808', foreground='white', borderwidth=2)
end_date.place(relx=0.75, rely=0.6, anchor="center")

# Create dropdown menus for selecting start and end times with AM and PM
start_time_options = ["12:00 AM", "01:00 AM", "02:00 AM", "03:00 AM", "04:00 AM", "05:00 AM", "06:00 AM", "07:00 AM",
                      "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM",
                      "04:00 PM", "05:00 PM", "06:00 PM", "07:00 PM", "08:00 PM", "09:00 PM", "10:00 PM", "11:00 PM"]

start_time = tk.StringVar(window)
start_time.set("03:00 AM")  # Default value set to 3 AM

start_time_menu = tk.OptionMenu(window, start_time, *start_time_options)
start_time_menu.config(bg="#444444", fg="white", font=("Arial", 12), relief=tk.FLAT)
start_time_menu.place(relx=0.25, rely=0.7, anchor="center")

end_time = tk.StringVar(window)
end_time.set("03:00 AM")  # Default value set to 3 AM

end_time_menu = tk.OptionMenu(window, end_time, *start_time_options)
end_time_menu.config(bg="#444444", fg="white", font=("Arial", 12), relief=tk.FLAT)
end_time_menu.place(relx=0.75, rely=0.7, anchor="center")

# Create a label to display the selected file
selected_file_label = tk.Label(window, text="No file selected", bg="#111111", fg="white", font=("Arial", 12), highlightbackground="#111111", highlightthickness=0)
selected_file_label.place(relx=0.5, rely=0.8, anchor="center")

# Create a label to display the result with no background
result_label = tk.Label(window, text="", bg="#111111", fg="white", font=("Arial", 14), highlightbackground="#111111", highlightthickness=0)
result_label.place(relx=0.5, rely=0.1, anchor="center")

# Create a button to browse for a file
browse_button = tk.Button(window, text="Browse", command=browse_file)
browse_button.config(bg="#e50914", fg="white", font=("Arial", 12), relief=tk.RAISED, cursor="hand2")
browse_button.place(relx=0.5, rely=0.85, anchor="center")

# Create a button to extract data from the selected file
extract_button = tk.Button(window, text="Extract Data", command=extract_data)
extract_button.config(bg="#e50914", fg="white", font=("Arial", 12), relief=tk.RAISED, cursor="hand2")
extract_button.place(relx=0.5, rely=0.9, anchor="center")

# Create a button to copy total seconds
copy_button = tk.Button(window, text="Copy Total Seconds", command=copy_total_seconds)
copy_button.config(bg="#e50914", fg="white", font=("Arial", 12), relief=tk.RAISED, cursor="hand2")
# Initially hide the copy button
copy_button.place_forget()

# Create a label to display the donation text with a copy button
donation_text = "CeoH3dk1VyCj5HHXfoBvBtvQZnvU5WCZMXzuV6Fq7ZGV"
donation_label = tk.Label(window, text=f"Donate to support this project: {donation_text} (click to copy)", bg="#111111", fg="white", font=("Arial", 12), cursor="hand2")
donation_label.place(relx=0.5, rely=0.95, anchor="center")

# Function to copy the donation text to clipboard
def copy_donation_text():
    window.clipboard_clear()
    window.clipboard_append(donation_text)
    messagebox.showinfo("Copied", f"Donation text ({donation_text}) copied to clipboard.")

# Bind the copy_donation_text function to the donation label
donation_label.bind("<Button-1>", lambda event: copy_donation_text())

# Run the Tkinter event loop
window.mainloop()
