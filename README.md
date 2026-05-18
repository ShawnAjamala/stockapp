# Supermarket Storage System
A desktop inventory management application built with Python Tkinter and MongoDB for tracking supermarket stock from warehouse to sales floor.
---

## Githup repository link
https://github.com/ShawnAjamala/stockapp
---

## Project Overview
The Supermarket Storage System is a desktop application that helps supermarket managers track inventory movements between the warehouse and the sales floor. The system distinguishes between two types of stock movements:

- Stock In (Increase) - When the supermarket buys products from suppliers and adds them to warehouse storage
- Stock Out (Decrease) - When the warehouse supplies products to the supermarket sales floor for customers to purchase

This application provides a graphical user interface for managing products, recording stock movements, and generating inventory reports.
---

## How It Works

The application connects to a MongoDB Atlas cloud database to store three collections:

1. Users Collection - Stores user accounts with hashed passwords for authentication
2. Products Collection - Stores product information including name, price, and current stock quantity
3. Transactions Collection - Records all stock movements with timestamps

When a user logs in, they can:
- Add new products to the inventory
- Record stock purchases from suppliers (increases quantity)
- Record stock supplies to the supermarket (decreases quantity)
- View all products with current stock levels
- See low stock warnings when quantity falls below a threshold
- Export inventory data to CSV files

---

## Features

Authentication System
- Login with email and password
- New user registration (full name, email, password)
- Password hashing for security
- Default admin account included

Product Management
- Add new products with name, price, and quantity
- Edit existing product information
- Delete products from inventory
- Search products by name

Stock Movement Tracking
- Stock In - Record purchases from suppliers (adds quantity)
- Stock Out - Record supplies to supermarket (subtracts quantity)
- Prevents negative stock quantities
- Timestamp recording for all transactions

Inventory Viewing
- Display all products in a table format
- Show current stock levels in real-time
- Highlight low stock items
- Calculate total inventory value

Reporting
- Export inventory to CSV file
- View transaction history
- Filter by date range

---

## Technology Stack

Backend
- Python 3.14 - Core programming language
- MongoDB Atlas - Cloud database for data persistence

Frontend
- Tkinter - Python's built-in GUI library
- Ttk - Themed Tkinter widgets for modern interface

Security
- Hashlib - Built-in Python library for password hashing
- Secrets - Built-in Python library for generating secure salts
---

## Installation Guide

Step 1: Install Python
Make sure Python 3.8 or higher is installed on your system. Download from python.org.

Step 2: Install MongoDB
Create a free MongoDB Atlas account at mongodb.com/atlas and set up a cluster. The connection string is provided in the code.

Step 3: Create Project Folder
Open terminal or command prompt and run:

mkdir supermarket_storage
cd supermarket_storage

Step 4: Create Virtual Environment

Step 5: Install Required Packages
pip install pymongo

Step 6: Create Project Files

Step 7: Set Database Connection
The db.py file already contains the MongoDB Atlas connection string. Replace it with your own if needed.

---

## Running the Application

Step 1: Activate Virtual Environment

Windows:
source venv/Scripts/activate

Mac/Linux:
source venv/bin/activate

Step 2: Run the Application
python main.py

Or directly:
python auth.py

Step 3: Login with Default Credentials
Email: admin@supermarket.com
Password: admin123

Or register a new account using the Register tab.

---
## Author
-Shawn Ajamala
