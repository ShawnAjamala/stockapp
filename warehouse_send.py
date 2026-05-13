import tkinter as tk
from tkinter import ttk, messagebox

class WarehouseSend(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.configure(bg='#F5F6FA')
        
        self.create_widgets()
    
    def create_widgets(self):
        header_frame = tk.Frame(self, bg='#FFFFFF')
        header_frame.pack(fill="x", pady=(0, 20))
        tk.Label(header_frame, text="SEND STOCK TO SUPERMARKET", font=("Segoe UI", 20, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=20)
        
        content_frame = tk.Frame(self, bg='#FFFFFF')
        content_frame.pack(fill="both", expand=True)
        
        tk.Label(content_frame, text="Send Stock Feature", font=("Segoe UI", 14), 
                bg='#FFFFFF', fg='#7F8C8D').pack(expand=True)
        tk.Label(content_frame, text="Coming Soon in Phase 3", font=("Segoe UI", 11), 
                bg='#FFFFFF', fg='#95A5A6').pack()