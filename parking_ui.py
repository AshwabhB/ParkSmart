import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, time

class ParkingUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SJSU Parking Garage Selector")
        self.root.geometry("450x600")
        self.root.configure(bg='#f0f0f0')  
        
       
        main_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        
        title_frame = tk.Frame(main_frame, bg='#003366')  
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(title_frame, 
                             text="SJSU Parking Garage Status",
                             font=('Arial', 16, 'bold'),
                             fg='white',
                             bg='#003366',
                             pady=10)
        title_label.pack()
        
        
        garage_frame = tk.LabelFrame(main_frame, 
                                   text="Select Garage", 
                                   font=('Arial', 12, 'bold'),
                                   bg='#f0f0f0',
                                   fg='#003366',
                                   padx=15,
                                   pady=10)
        garage_frame.pack(fill='x', pady=(0, 20))
        
        
        self.garage_var = tk.StringVar()
        self.garages = ['North Garage', 'South Garage', 'West Garage', 'South Campus Garage']
        
        for idx, garage in enumerate(self.garages):
            rb = tk.Radiobutton(garage_frame,
                              text=garage,
                              variable=self.garage_var,
                              value=garage,
                              font=('Arial', 11),
                              bg='#f0f0f0',
                              activebackground='#e1e1e1',
                              command=self.update_selection)
            rb.pack(anchor='w', pady=5)
        
        
        time_frame = tk.LabelFrame(main_frame,
                                 text="Select Time",
                                 font=('Arial', 12, 'bold'),
                                 bg='#f0f0f0',
                                 fg='#003366',
                                 padx=15,
                                 pady=10)
        time_frame.pack(fill='x', pady=(0, 20))
        
        
        time_container = tk.Frame(time_frame, bg='#f0f0f0')
        time_container.pack(fill='x', padx=5, pady=5)
        
        
        hour_frame = tk.Frame(time_container, bg='#f0f0f0')
        hour_frame.pack(side='left', padx=5)
        
        tk.Label(hour_frame,
                text="Hour:",
                font=('Arial', 11),
                bg='#f0f0f0').pack(side='left', padx=(0, 5))
        
        self.time_var = tk.StringVar()
        hours = [f"{h:02d}:00" for h in range(1, 13)]
        time_dropdown = ttk.Combobox(hour_frame,
                                   textvariable=self.time_var,
                                   values=hours,
                                   width=8,
                                   font=('Arial', 11))
        time_dropdown.pack(side='left')
        time_dropdown.set("Hour")
        
        ampm_frame = tk.Frame(time_container, bg='#f0f0f0')
        ampm_frame.pack(side='left', padx=20)
        
        self.ampm_var = tk.StringVar(value="AM")
        
        am_rb = tk.Radiobutton(ampm_frame,
                              text="AM",
                              variable=self.ampm_var,
                              value="AM",
                              font=('Arial', 11, 'bold'),
                              bg='#f0f0f0',
                              activebackground='#e1e1e1')
        am_rb.pack(side='left', padx=5)
        
        pm_rb = tk.Radiobutton(ampm_frame,
                              text="PM",
                              variable=self.ampm_var,
                              value="PM",
                              font=('Arial', 11, 'bold'),
                              bg='#f0f0f0',
                              activebackground='#e1e1e1')
        pm_rb.pack(side='left', padx=5)
        
        
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=20)
        
        self.go_button = tk.Button(button_frame,
                                 text="Check Status",
                                 font=('Arial', 12, 'bold'),
                                 bg='#003366',
                                 fg='white',
                                 activebackground='#004080',
                                 activeforeground='white',
                                 padx=20,
                                 pady=10,
                                 cursor='hand2',
                                 relief=tk.RAISED,
                                 command=self.on_go_click)
        self.go_button.pack(expand=True)
        
        
        result_frame = tk.Frame(main_frame, bg='#003366', padx=2, pady=2)
        result_frame.pack(fill='x', pady=(0, 20))
        
        self.result_var = tk.StringVar()
        self.result_label = tk.Label(result_frame,
                                   textvariable=self.result_var,
                                   font=('Arial', 11),
                                   wraplength=350,
                                   bg='white',
                                   fg='#003366',
                                   pady=10)
        self.result_label.pack(fill='both', expand=True)
    
    def update_selection(self):
        self.result_var.set("")
    
    def on_go_click(self):
        garage = self.garage_var.get()
        selected_time = self.time_var.get()
        ampm = self.ampm_var.get()
        
        if not garage or selected_time == "Hour":
            messagebox.showwarning("Warning", "Please select both a garage and time!")
            return
        
        self.result_var.set(f"You have selected {garage} for {selected_time} {ampm}. The Garage is 78% Full. Best option is to park in the South Campus Garage.")

def main():
    root = tk.Tk()
    app = ParkingUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 