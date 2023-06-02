import tkinter as tk
from tkinter import messagebox

# root = tk.Tk()

# #sets the window's size to be 1600x900
# root.geometry("800x500")

# #set the title
# root.title("My First GUI")

# #open a window
# root.mainloop()

class firstGUI:
    def __init__(self) -> None:
        self.root = tk.Tk()

        self.label = tk.Label(self.root, text="Your Message", font=('Arial', 18))
        self.label.pack(padx=10, pady=5)

        self.textbox = tk.Text(self.root, height=5, font=('Arial', 18))
        self.textbox.pack(padx=5, pady=10)

        self.check_state = tk.IntVar()

        self.check = tk.Checkbutton(self.root, text = "Show Message in a Messagebox?", font=('Arial', 18), variable=self.check_state)
        self.check.pack(padx=10, pady=10)

        # DON'T ADD () AT THE END OF COMMAND. 
        # we're not calling show_message directly, we're passing the function as a parameter to button
        self.button = tk.Button(self.root, text = "Show Message", font=('Arial', 18), command=self.show_message)
        self.button.pack(padx=10, pady=10)

        self.root.mainloop()

    def show_message(self):
        #print("Hello World!")
        #print(self.check_state.get())
        
        #check if self.check_state (type IntVar) is 1 or 0
        
        if (self.check_state.get() == 0): #user doesn't want message to be shown in a messagebox
            #parameters in get are the indexes for the message. 1.0 means start of the text box, tk.END is the end of the text box
            print(self.textbox.get('1.0', tk.END))
        else:
            messagebox.showinfo(title="Your Message", message=self.textbox.get('1.0', tk.END))

    

firstGUI()