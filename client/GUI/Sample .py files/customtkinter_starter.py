import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

def submit_fasta(event = None):
    filename = filedialog.askopenfilename()
    print(f'Selected: {filename}')

# root = tk.Tk()
# root.geometry("500x500")
# button = tk.Button(root, text='Open', command=submit)
# button.pack()

# root.mainloop()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("800x500")

frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill = "both", expand = True)

label = ctk.CTkLabel(master=frame, text = "Concrete-ML FHE SARS-CoV 2 Classifier (Client-Side)", font=('Roboto', 18))
label.pack(pady=12, padx=10)

dashing_frame = ctk.CTkFrame(master=frame)
dashing_frame.grid_columnconfigure((0,1,2,3), weight=1)
dashing_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)

dashing_label = ctk.CTkLabel(master=dashing_frame, text="Select a file for dashing:")
dashing_label.grid(row=0, column=0, padx=10, pady=(10,10))
dashing_entry = ctk.CTkEntry(master=dashing_frame, placeholder_text="", state="disabled")
dashing_entry.grid(row=1, column=0, padx=10, pady=(10,10))
dashing_browse_button = ctk.CTkButton(master=dashing_frame, str="Browse...")
dashing_browse_button.grid(row=1, column=0, padx=10, pady=(10,10))
dashing_frame.pack(pady=20, padx = 60)


root.mainloop()

