import tkinter as tk
from tkinter import messagebox

class SupermarketProfile(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.parent = parent
        self.configure(bg='#F5F6FA')
        
        self.create_widgets()
    
    def create_widgets(self):
        header_frame = tk.Frame(self, bg='#FFFFFF')
        header_frame.pack(fill="x", pady=(0, 20))
        tk.Label(header_frame, text="MY PROFILE", font=("Segoe UI", 20, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=20)
        
        profile_card = tk.Frame(self, bg='#FFFFFF', relief='raised', bd=1)
        profile_card.pack(pady=20, padx=100, fill="both", expand=True)
        
        details_frame = tk.Frame(profile_card, bg='#FFFFFF')
        details_frame.pack(pady=40, padx=50)
        
        tk.Label(details_frame, text="USER INFORMATION", font=("Segoe UI", 16, "bold"), 
                bg='#FFFFFF', fg='#E67E22').pack(pady=(0, 25))
        
        fields = [
            ("Full Name:", self.user['fullname']),
            ("Email Address:", self.user['email']),
            ("Role:", self.user['role'].upper()),
            ("Account Type:", "Supermarket Administrator")
        ]
        
        for label, value in fields:
            row_frame = tk.Frame(details_frame, bg='#FFFFFF')
            row_frame.pack(fill='x', pady=12)
            tk.Label(row_frame, text=label, font=("Segoe UI", 11, "bold"), 
                    bg='#FFFFFF', fg='#2C3E50', width=18, anchor='w').pack(side='left')
            tk.Label(row_frame, text=value, font=("Segoe UI", 11), 
                    bg='#FFFFFF', fg='#5D4E37', anchor='w').pack(side='left', padx=(15, 0))
        
        btn_frame = tk.Frame(profile_card, bg='#FFFFFF')
        btn_frame.pack(pady=25)
        
        def delete_account():
            if messagebox.askyesno("Delete Account", "Are you sure you want to delete your account? This action cannot be undone!"):
                messagebox.showinfo("Account Deleted", "Your account has been deleted successfully")
                self.logout()
        
        tk.Button(btn_frame, text="DELETE ACCOUNT", command=delete_account,
                 bg='#E74C3C', fg='white', font=("Segoe UI", 10, "bold"), 
                 relief='flat', cursor='hand2', padx=30, pady=8).pack(side='left', padx=10)
    
    def logout(self):
        self.winfo_toplevel().destroy()
        from auth import AuthWindow
        root = tk.Tk()
        AuthWindow(root)
        root.mainloop()