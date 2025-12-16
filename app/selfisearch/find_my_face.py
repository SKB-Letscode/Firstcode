
#====================================================================================
# Author: Sara 
# Created on: 21 Nov 2025
# Brief: This Windows UI Application is an Utility to Seearch my photos.
# Test ABCD from persoanl email committ
#====================================================================================
import tkinter as tk
from tkinter import filedialog, messagebox
import requests
from PIL import Image, ImageTk
import io

API_URL = "http://localhost:8000/search-face"

def search_face(image_path):
    with open(image_path, 'rb') as f:
        response = requests.post(API_URL, files={"file": f})
    if response.status_code == 200:
        results = response.json().get("matches", [])
        display_results(results)
    else:
        messagebox.showerror("Error", "Failed to search face")

def display_results(results):
    for widget in result_frame.winfo_children():
        widget.destroy()
    for match in results:
        tk.Label(result_frame, text=f"{match['FileName']} (Distance: {match['Distance']:.2f})").pack()

def select_image():
    image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
    if image_path:
        search_face(image_path)

root = tk.Tk()
root.title("Face Search")
tk.Button(root, text="Select Selfie and Search", command=select_image).pack(pady=10)
result_frame = tk.Frame(root)
result_frame.pack(pady=10)
root.mainloop()
