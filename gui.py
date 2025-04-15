# gui.py
import tkinter as tk
from tkinter import ttk
from tkinter import Label, Button, Entry, font, messagebox, Toplevel
from datetime import date, datetime
import random
import string
from connection import (
    login_user, login_admin, register_user, search_train_by_number,
    search_train_by_location, book_ticket, cancel_ticket,
    get_booking_by_pnr, get_all_users, update_user_password,
    delete_user_from_db, add_train, update_train, delete_train,
    add_station, get_all_stations, get_all_trains
)

# New color palette
BG_COLOR = "#0F0F1A"
TEXT_COLOR = "#EAEAEA"
BTN_COLOR = "#3A7CA5"
BTN_HOVER_COLOR = "#2F5D81"
ENTRY_BG = "#1E1E2E"
ENTRY_FG = "#FFFFFF"
ACCENT_COLOR = "#FF0000"

WINDOW_SIZE = "800x600"  
BTN_HEIGHT = 2
BTN_WIDTH = 25  
ENTRY_WIDTH = 25  

# Global variables to store current user info
current_user = None

# Updated login/signup handlers
def handle_login(username_entry, password_entry):
    username = username_entry.get()
    password = password_entry.get()

    if(username == "" or password == ""):
        messagebox.showerror("Error", "Please fill in all fields")
        return
    
    user = login_user(username, password)

    if user:
        global current_user
        current_user = user
        userEntryPage()
    else:
        messagebox.showerror("Login Failed", "Invalid credentials")

def handle_admin_login(username_entry, password_entry):
    username = username_entry.get()
    password = password_entry.get()

    if(username == "" or password == ""):
        messagebox.showerror("Error", "Please fill in all fields")
        return
    
    admin = login_admin(username, password)

    if admin:
        adminEntryPage()
    else:
        messagebox.showerror("Login Failed", "Invalid admin credentials")

def handle_signup(username_entry, password_entry, confirm_password_entry):
    username = username_entry.get()
    password = password_entry.get()
    confirm_password = confirm_password_entry.get()
    
    if(username == "" or password == "" or confirm_password == ""):
        messagebox.showerror("Error", "Please fill in all fields")
        return
    
    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match")
        return
    
    try:
        register_user(username, password)
        messagebox.showinfo("Success", "User registered successfully")
        userLoginPage()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Updated search and booking functions
def handle_search_by_number(entry):
    train_no = entry.get()
    if not train_no:
        messagebox.showerror("Error", "Please enter a train number")
        return
        
    result = search_train_by_number(train_no)
    display_table(result, heading_text="Search Result - Train No.", back_command=searchTrain)

def handle_search_by_location(source_entry, dest_entry):
    src = source_entry.get()
    dest = dest_entry.get()
    
    if not src or not dest:
        messagebox.showerror("Error", "Please enter both source and destination")
        return
        
    result = search_train_by_location(src, dest)
    display_table(result, heading_text="Search Result - Location", back_command=searchTrain)

def handle_book_ticket(train_id_entry, travel_date_entry, passengers_frame):
    if not current_user:
        messagebox.showerror("Error", "You must be logged in to book tickets")
        return
        
    train_id = train_id_entry.get()
    travel_date_str = travel_date_entry.get()
    
    if not train_id or not travel_date_str:
        messagebox.showerror("Error", "Please enter train ID and travel date")
        return
    
    try:
        travel_date = datetime.strptime(travel_date_str, "%Y-%m-%d").date()
    except ValueError:
        messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
        return
    
    # Collect passenger information from input fields
    passenger_list = []
    for i, passenger_entries in enumerate(passengers_frame.winfo_children()):
        if isinstance(passenger_entries, tk.Frame):
            name = ""
            age = 0
            gender = ""
            
            for entry in passenger_entries.winfo_children():
                if isinstance(entry, tk.Entry):
                    tag = entry.winfo_name()
                    value = entry.get()
                    
                    if "name" in tag:
                        name = value
                    elif "age" in tag:
                        try:
                            age = int(value)
                        except ValueError:
                            messagebox.showerror("Error", f"Invalid age for passenger {i+1}")
                            return
                    elif "gender" in tag:
                        gender = value
            
            if name and age and gender:
                passenger_list.append({
                    "name": name,
                    "age": age,
                    "gender": gender
                })
    
    if not passenger_list:
        messagebox.showerror("Error", "No passenger information provided")
        return
    
    try:
        booking_date = date.today()
        booking_id, pnr = book_ticket(
            current_user['user_id'], 
            int(train_id), 
            travel_date, 
            booking_date, 
            passenger_list
        )
        messagebox.showinfo("Success", f"Ticket(s) booked successfully!\nPNR: {pnr}")
        userEntryPage()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to book ticket: {str(e)}")

def handle_check_status(pnr_entry):
    pnr = pnr_entry.get()
    if not pnr:
        messagebox.showerror("Error", "Please enter a PNR number")
        return
        
    booking = get_booking_by_pnr(pnr)
    
    if booking:
        # Convert to list of dictionaries for the display_table function
        booking_list = [{
            'PNR': booking['pnr_number'],
            'Train': f"{booking['train_number']} - {booking['train_name']}",
            'Travel Date': booking['travel_date'],
            'Status': booking['status'],
            'Passengers': len(booking['passengers'])
        }]
        display_table(booking_list, heading_text="Booking Status", back_command=bookingStatus)
        
        # Show passenger details in a new window
        show_passenger_details(booking['passengers'])
    else:
        messagebox.showinfo("No Results", "No booking found with that PNR")

def show_passenger_details(passengers):
    passenger_window = Toplevel(root)
    passenger_window.title("Passenger Details")
    passenger_window.geometry("600x400")
    passenger_window.configure(bg=BG_COLOR)
    
    Label(passenger_window, text="Passenger Details", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
    
    # Create table for passengers
    columns = ("Name", "Age", "Gender")
    tree = ttk.Treeview(passenger_window, columns=columns, show="headings", style="mystyle.Treeview")
    tree.pack(pady=20, fill="both", expand=True)
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    
    for passenger in passengers:
        tree.insert("", "end", values=(
            passenger['name'],
            passenger['age'],
            passenger['gender']
        ))
    
    Button(passenger_window, text="Close", command=passenger_window.destroy,
           bg=ACCENT_COLOR, fg="white", font=LABEL_FONT, bd=0).pack(pady=20)

def handle_cancel_ticket(pnr_entry, reason_entry):
    pnr = pnr_entry.get()
    reason = reason_entry.get() if reason_entry.get() else "User Request"
    
    if not pnr:
        messagebox.showerror("Error", "Please enter a PNR number")
        return
    
    # Confirm cancellation
    confirm = messagebox.askyesno("Confirm Cancellation", 
                                "Are you sure you want to cancel this ticket? This action cannot be undone.")
    if not confirm:
        return
    
    today = date.today()
    success = cancel_ticket(pnr, reason, today)
    
    if success:
        messagebox.showinfo("Success", "Ticket cancelled successfully")
        userEntryPage()
    else:
        messagebox.showerror("Error", "Failed to cancel ticket. Invalid PNR.")

# User management functions
def handle_add_user(username_entry, password_entry):
    username = username_entry.get()
    password = password_entry.get()
    
    if not username or not password:
        messagebox.showerror("Error", "Please fill in all fields")
        return
    
    try:
        register_user(username, password)
        messagebox.showinfo("Success", "User added successfully")
        manageUsersPage()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add user: {str(e)}")

def handle_update_user(username_entry, new_password_entry):
    username = username_entry.get()
    new_password = new_password_entry.get()
    
    if not username or not new_password:
        messagebox.showerror("Error", "Please fill in all fields")
        return
    
    try:
        update_user_password(username, new_password)
        messagebox.showinfo("Success", "User password updated successfully")
        manageUsersPage()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update user: {str(e)}")

def handle_delete_user(username_entry):
    username = username_entry.get()
    
    if not username:
        messagebox.showerror("Error", "Please enter a username")
        return
    
    confirm = messagebox.askyesno("Confirm Deletion", 
                                f"Are you sure you want to delete user '{username}'? This action cannot be undone.")
    if not confirm:
        return
    
    try:
        delete_user_from_db(username)
        messagebox.showinfo("Success", "User deleted successfully")
        manageUsersPage()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete user: {str(e)}")

# Train management functions
def handle_add_train(entries):
    train_data = {
        'train_number': entries['train_number'].get(),
        'train_name': entries['train_name'].get(),
        'source_id': entries['source_id'].get(),
        'destination_id': entries['destination_id'].get(),
        'departure_time': entries['departure_time'].get(),
        'arrival_time': entries['arrival_time'].get(),
        'travel_days': entries['travel_days'].get()
    }
    
    # Validate input
    for key, value in train_data.items():
        if not value:
            messagebox.showerror("Error", f"Please enter {key.replace('_', ' ')}")
            return
    
    try:
        source_id = int(train_data['source_id'])
        destination_id = int(train_data['destination_id'])
        
        add_train(
            train_data['train_number'],
            train_data['train_name'],
            source_id,
            destination_id,
            train_data['departure_time'],
            train_data['arrival_time'],
            train_data['travel_days']
        )
        messagebox.showinfo("Success", "Train added successfully")
        manageSchedules()
    except ValueError:
        messagebox.showerror("Error", "Station IDs must be integers")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add train: {str(e)}")

def handle_update_train(entries):
    train_id = entries['train_id'].get()
    
    if not train_id:
        messagebox.showerror("Error", "Please enter train ID")
        return
    
    try:
        train_id = int(train_id)
        update_data = {}
        
        for key, entry in entries.items():
            if key != 'train_id' and entry.get():
                if key in ['source_id', 'destination_id']:
                    update_data[key] = int(entry.get())
                else:
                    update_data[key] = entry.get()
        
        if not update_data:
            messagebox.showerror("Error", "Please enter at least one field to update")
            return
        
        update_train(train_id, **update_data)
        messagebox.showinfo("Success", "Train updated successfully")
        manageSchedules()
    except ValueError:
        messagebox.showerror("Error", "IDs must be integers")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update train: {str(e)}")

def handle_delete_train(train_id_entry):
    train_id = train_id_entry.get()
    
    if not train_id:
        messagebox.showerror("Error", "Please enter train ID")
        return
    
    confirm = messagebox.askyesno("Confirm Deletion", 
                                f"Are you sure you want to delete train ID {train_id}? This action cannot be undone.")
    if not confirm:
        return
    
    try:
        train_id = int(train_id)
        delete_train(train_id)
        messagebox.showinfo("Success", "Train deleted successfully")
        manageSchedules()
    except ValueError:
        messagebox.showerror("Error", "Train ID must be an integer")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete train: {str(e)}")

def view_all_trains():
    trains = get_all_trains()
    display_table(trains, heading_text="All Trains", back_command=manageSchedules)

# Station management functions
def handle_add_station(station_name_entry, station_code_entry):
    station_name = station_name_entry.get()
    station_code = station_code_entry.get()
    
    if not station_name or not station_code:
        messagebox.showerror("Error", "Please enter station name and code")
        return
    
    try:
        add_station(station_name, station_code)
        messagebox.showinfo("Success", "Station added successfully")
        manageSchedules()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add station: {str(e)}")
        
def display_stations():
    stations = get_all_stations()
    
    if not stations:
        messagebox.showinfo("No Stations", "No stations found in the database")
        return
    
    # Convert to list of dictionaries for display_table
    station_list = [{'ID': s[0], 'Name': s[1]} for s in stations]
    display_table(station_list, heading_text="Stations", back_command=manageSchedules)

# UI Setup
root = tk.Tk()
root.geometry(WINDOW_SIZE)
root.title("FastLink Railway System")

try:
    root.iconbitmap("train_icon.ico")  
except tk.TclError:
    pass  

root.configure(bg=BG_COLOR)

HEADING_FONT = font.Font(family="Montserrat", size=42, weight="bold") 
BUTTON_FONT = font.Font(family="Roboto", size=14, weight="bold")
LABEL_FONT = font.Font(family="Lato", size=14)
ENTRY_FONT = font.Font(family="Consolas", size=14)

style = ttk.Style()
style.configure("mystyle.Treeview", font=('Calibri', 14), rowheight=30)
style.configure("mystyle.Treeview.Heading", font=('Calibri', 16, 'bold'))


def on_enter(e):
    e.widget["background"] = BTN_HOVER_COLOR

def on_leave(e):
    e.widget["background"] = BTN_COLOR

def create_button(text, command=None):
    btn = Button(root, text=text, command=command, bg=BTN_COLOR, fg=TEXT_COLOR,
                 width=BTN_WIDTH, height=BTN_HEIGHT, font=BUTTON_FONT, bd=0, activebackground=BTN_HOVER_COLOR,
                 relief="flat")  
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def create_back_button(command):
    btn = Button(root, text="Back", command=command, font=LABEL_FONT, bg=ACCENT_COLOR, fg="white",
                 width=10, bd=0, relief="flat", activebackground="#D30000") 
    return btn

def clear_root():
    for widget in root.winfo_children():
        widget.destroy()

def entryPage():
    clear_root()
    heading = Label(root, text="Welcome to FastLink", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=60)

    create_button("Admin", adminLoginPage).pack(pady=15)
    create_button("User", userPage).pack(pady=15)

def userPage():
    clear_root()
    heading = Label(root, text="New User?", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=50)

    create_button("Log In", userLoginPage).pack(pady=15)
    create_button("Sign Up", signUpPage).pack(pady=15)

    create_back_button(entryPage).pack(pady=20)

def userLoginPage():
    clear_root()
    heading = Label(root, text="Enter Log In Details", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=50)

    username_frame = tk.Frame(root, bg=BG_COLOR)
    username_frame.pack(pady=10)
    Label(username_frame, text="Username", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=10, anchor="w").pack(side="left", padx=5)
    username_entry = Entry(username_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG, highlightthickness=1, highlightcolor=ACCENT_COLOR)
    username_entry.pack(side="left", padx=5)

    password_frame = tk.Frame(root, bg=BG_COLOR)
    password_frame.pack(pady=10)
    Label(password_frame, text="Password", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=10, anchor="w").pack(side="left", padx=5)
    password_entry = Entry(password_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG, show="*", highlightthickness=1, highlightcolor=ACCENT_COLOR)
    password_entry.pack(side="left", padx=5)

    create_button("Log In", lambda: handle_login(username_entry, password_entry)).pack(pady=20)
    create_back_button(userPage).pack(pady=10)

def adminLoginPage():
    clear_root()
    heading = Label(root, text="Admin Log In", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=50)

    username_frame = tk.Frame(root, bg=BG_COLOR)
    username_frame.pack(pady=10)
    Label(username_frame, text="Username", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=10, anchor="w").pack(side="left", padx=5)
    username_entry = Entry(username_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG, highlightthickness=1, highlightcolor=ACCENT_COLOR)
    username_entry.pack(side="left", padx=5)

    password_frame = tk.Frame(root, bg=BG_COLOR)
    password_frame.pack(pady=10)
    Label(password_frame, text="Password", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=10, anchor="w").pack(side="left", padx=5)
    password_entry = Entry(password_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG, show="*", highlightthickness=1, highlightcolor=ACCENT_COLOR)
    password_entry.pack(side="left", padx=5)

    create_button("Log In", lambda: handle_admin_login(username_entry, password_entry)).pack(pady=20)
    create_back_button(entryPage).pack(pady=10)

def signUpPage():
    clear_root()
    heading = Label(root, text="Sign Up", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=40)

    username_frame = tk.Frame(root, bg=BG_COLOR)
    username_frame.pack(pady=5)
    Label(username_frame, text="Username", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=15, anchor="w").pack(side="left", padx=5)
    username_entry = Entry(username_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG, highlightthickness=1, highlightcolor=ACCENT_COLOR)
    username_entry.pack(side="left", padx=5)

    password_frame = tk.Frame(root, bg=BG_COLOR)
    password_frame.pack(pady=5)
    Label(password_frame, text="Password", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=15, anchor="w").pack(side="left", padx=5)
    password_entry = Entry(password_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG, show="*", highlightthickness=1, highlightcolor=ACCENT_COLOR)
    password_entry.pack(side="left", padx=5)

    confirm_password_frame = tk.Frame(root, bg=BG_COLOR)
    confirm_password_frame.pack(pady=5)
    Label(confirm_password_frame, text="Confirm Password", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=15, anchor="w").pack(side="left", padx=5)
    confirm_password_entry = Entry(confirm_password_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG, show="*", highlightthickness=1, highlightcolor=ACCENT_COLOR)
    confirm_password_entry.pack(side="left", padx=5)

    create_button("Sign Up", lambda: handle_signup(username_entry, password_entry, confirm_password_entry)).pack(pady=20)
    create_back_button(userPage).pack(pady=10)

def userEntryPage():
    clear_root()
    heading = Label(root, text=f"Welcome {current_user['username']}", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=50)

    create_button("Search Trains", searchTrain).pack(pady=10)
    create_button("Book Ticket", bookTicket).pack(pady=10)
    create_button("Check Booking Status", bookingStatus).pack(pady=10)
    create_button("Cancel Ticket", cancelTicket).pack(pady=10)
    create_button("Log Out", lambda: logout_user()).pack(pady=20)

def logout_user():
    global current_user
    current_user = None
    entryPage()

def display_table(data, heading_text="Results", back_command=userEntryPage):
    clear_root()
    heading = Label(root, text=heading_text, font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=20)

    if not data:
        Label(root, text="No data found.", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        create_back_button(back_command).pack(pady=20)
        return

    table_frame = tk.Frame(root, bg=BG_COLOR)
    table_frame.pack(pady=10, fill="both", expand=True)

    canvas = tk.Canvas(table_frame, bg=BG_COLOR, highlightthickness=0)
    scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Get column headers
    if data and isinstance(data[0], dict):
        keys = list(data[0].keys())
        
        for idx, key in enumerate(keys):
            Label(scrollable_frame, text=key, font=LABEL_FONT, bg=BTN_COLOR, fg="white", 
                  width=20, borderwidth=1, relief="solid").grid(row=0, column=idx)

        # Data rows
        for i, row in enumerate(data):
            for j, key in enumerate(keys):
                value = row[key]
                Label(scrollable_frame, text=str(value), font=ENTRY_FONT, bg=ENTRY_BG, 
                      fg=TEXT_COLOR, width=20, borderwidth=1, relief="ridge").grid(row=i + 1, column=j)

    create_back_button(back_command).pack(pady=20)

def adminEntryPage():
    clear_root()
    heading = Label(root, text="Welcome Admin", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=50)

    create_button("Manage Users", manageUsersPage).pack(pady=10)
    create_button("Manage Schedules", manageSchedules).pack(pady=10)
    create_button("Manage Stations", manageStations).pack(pady=10)
    create_button("Log Out", entryPage).pack(pady=20)

def bookTicket():
    clear_root()
    heading = Label(root, text="Book Your Ticket", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=30)

    # Train ID
    train_id_frame = tk.Frame(root, bg=BG_COLOR)
    train_id_frame.pack(pady=5)
    Label(train_id_frame, text="Train ID", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left", padx=5)
    train_id_entry = Entry(train_id_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    train_id_entry.pack(side="left", padx=5)

    # Travel Date
    date_frame = tk.Frame(root, bg=BG_COLOR)
    date_frame.pack(pady=5)
    Label(date_frame, text="Travel Date", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left", padx=5)
    travel_date_entry = Entry(date_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    travel_date_entry.pack(side="left", padx=5)
    Label(date_frame, text="(YYYY-MM-DD)", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(side="left", padx=5)

    # Passenger Information
    passenger_heading = Label(root, text="Passenger Information", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    passenger_heading.pack(pady=10)

    # Create a frame for passengers
    passengers_frame = tk.Frame(root, bg=BG_COLOR)
    passengers_frame.pack(pady=5, fill="both", expand=True)

    # Add a single passenger row by default
    add_passenger_row(passengers_frame, 1)

    # Button to add more passengers
    add_passenger_btn = Button(root, text="+ Add Passenger", command=lambda: add_passenger_row(passengers_frame, len(passengers_frame.winfo_children())+1),
                              bg=BTN_COLOR, fg=TEXT_COLOR, font=LABEL_FONT, bd=0)
    add_passenger_btn.pack(pady=10)

    # Book button
    create_button("Book Ticket", lambda: handle_book_ticket(train_id_entry, travel_date_entry, passengers_frame)).pack(pady=10)
    create_back_button(userEntryPage).pack(pady=10)

def cancelTicket():
    clear_root()
    heading = Label(root, text="Cancel Your Ticket", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=40)

    pnr_frame = tk.Frame(root, bg=BG_COLOR)
    pnr_frame.pack(pady=10)
    Label(pnr_frame, text="Enter PNR No.", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left", padx=5)
    pnr_entry = Entry(pnr_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG, highlightthickness=1, highlightcolor=ACCENT_COLOR)
    pnr_entry.pack(side="left", padx=5)

    reason_frame = tk.Frame(root, bg=BG_COLOR)
    reason_frame.pack(pady=10)
    Label(reason_frame, text="Reason", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left", padx=5)
    reason_entry = Entry(reason_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG, highlightthickness=1, highlightcolor=ACCENT_COLOR)
    reason_entry.pack(side="left", padx=5)

    create_button("Cancel Ticket", lambda: handle_cancel_ticket(pnr_entry, reason_entry)).pack(pady=20)
    create_back_button(userEntryPage).pack(pady=10)
    
def bookingStatus():
    clear_root()
    heading = Label(root, text="Booking Status", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=40)

    pnr_frame = tk.Frame(root, bg=BG_COLOR)
    pnr_frame.pack(pady=10)
    Label(pnr_frame, text="Enter PNR No.", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left", padx=5)
    pnr_entry = Entry(pnr_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG, highlightthickness=1, highlightcolor=ACCENT_COLOR)
    pnr_entry.pack(side="left", padx=5)

    create_button("Search", lambda: handle_check_status(pnr_entry)).pack(pady=20)
    create_back_button(userEntryPage).pack(pady=10)
    
def manageUsersPage():
    clear_root()
    heading = Label(root, text="Manage Users", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=30)

    # User management options
    create_button("Add User", addUserPage).pack(pady=10)
    create_button("Update User Password", updateUserPage).pack(pady=10)
    create_button("Delete User", deleteUserPage).pack(pady=10)
    create_button("View All Users", viewAllUsers).pack(pady=10)
    
    create_back_button(adminEntryPage).pack(pady=20)

def addUserPage():
    clear_root()
    heading = Label(root, text="Add New User", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=40)

    username_frame = tk.Frame(root, bg=BG_COLOR)
    username_frame.pack(pady=10)
    Label(username_frame, text="Username", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left", padx=5)
    username_entry = Entry(username_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    username_entry.pack(side="left", padx=5)

    password_frame = tk.Frame(root, bg=BG_COLOR)
    password_frame.pack(pady=10)
    Label(password_frame, text="Password", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left", padx=5)
    password_entry = Entry(password_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG, show="*")
    password_entry.pack(side="left", padx=5)

    create_button("Add User", lambda: handle_add_user(username_entry, password_entry)).pack(pady=20)
    create_back_button(manageUsersPage).pack(pady=10)

def updateUserPage():
    clear_root()
    heading = Label(root, text="Update User Password", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=40)

    username_frame = tk.Frame(root, bg=BG_COLOR)
    username_frame.pack(pady=10)
    Label(username_frame, text="Username", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=15, anchor="w").pack(side="left", padx=5)
    username_entry = Entry(username_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    username_entry.pack(side="left", padx=5)

    new_password_frame = tk.Frame(root, bg=BG_COLOR)
    new_password_frame.pack(pady=10)
    Label(new_password_frame, text="New Password", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=15, anchor="w").pack(side="left", padx=5)
    new_password_entry = Entry(new_password_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG, show="*")
    new_password_entry.pack(side="left", padx=5)

    create_button("Update Password", lambda: handle_update_user(username_entry, new_password_entry)).pack(pady=20)
    create_back_button(manageUsersPage).pack(pady=10)

def deleteUserPage():
    clear_root()
    heading = Label(root, text="Delete User", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=40)

    username_frame = tk.Frame(root, bg=BG_COLOR)
    username_frame.pack(pady=10)
    Label(username_frame, text="Username", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left", padx=5)
    username_entry = Entry(username_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    username_entry.pack(side="left", padx=5)

    create_button("Delete User", lambda: handle_delete_user(username_entry)).pack(pady=20)
    create_back_button(manageUsersPage).pack(pady=10)

def viewAllUsers():
    users = get_all_users()
    user_list = [{'Username': user[0], 'Password': '*' * len(user[1])} for user in users]
    display_table(user_list, heading_text="All Users", back_command=manageUsersPage)
    
def manageSchedules():
    clear_root()
    heading = Label(root, text="Manage Train Schedules", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=30)

    create_button("Add Train", addTrainPage).pack(pady=10)
    create_button("Update Train", updateTrainPage).pack(pady=10)
    create_button("Delete Train", deleteTrainPage).pack(pady=10)
    create_button("View All Trains", view_all_trains).pack(pady=10)
    
    create_back_button(adminEntryPage).pack(pady=20)

def addTrainPage():
    clear_root()
    heading = Label(root, text="Add New Train", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=20)

    entries = {}
    
    # Train Number
    train_number_frame = tk.Frame(root, bg=BG_COLOR)
    train_number_frame.pack(pady=5)
    Label(train_number_frame, text="Train Number", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=15, anchor="w").pack(side="left", padx=5)
    entries['train_number'] = Entry(train_number_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    entries['train_number'].pack(side="left", padx=5)

    # Train Name
    train_name_frame = tk.Frame(root, bg=BG_COLOR)
    train_name_frame.pack(pady=5)
    Label(train_name_frame, text="Train Name", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=15, anchor="w").pack(side="left", padx=5)
    entries['train_name'] = Entry(train_name_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    entries['train_name'].pack(side="left", padx=5)

    # Source ID
    source_id_frame = tk.Frame(root, bg=BG_COLOR)
    source_id_frame.pack(pady=5)
    Label(source_id_frame, text="Source ID", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=15, anchor="w").pack(side="left", padx=5)
    entries['source_id'] = Entry(source_id_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    entries['source_id'].pack(side="left", padx=5)

    # Destination ID
    dest_id_frame = tk.Frame(root, bg=BG_COLOR)
    dest_id_frame.pack(pady=5)
    Label(dest_id_frame, text="Destination ID", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=15, anchor="w").pack(side="left", padx=5)
    entries['destination_id'] = Entry(dest_id_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    entries['destination_id'].pack(side="left", padx=5)

    # Departure Time
    departure_frame = tk.Frame(root, bg=BG_COLOR)
    departure_frame.pack(pady=5)
    Label(departure_frame, text="Departure Time", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=15, anchor="w").pack(side="left", padx=5)
    entries['departure_time'] = Entry(departure_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    entries['departure_time'].pack(side="left", padx=5)

    # Arrival Time
    arrival_frame = tk.Frame(root, bg=BG_COLOR)
    arrival_frame.pack(pady=5)
    Label(arrival_frame, text="Arrival Time", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=15, anchor="w").pack(side="left", padx=5)
    entries['arrival_time'] = Entry(arrival_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    entries['arrival_time'].pack(side="left", padx=5)

    # Travel Days
    travel_days_frame = tk.Frame(root, bg=BG_COLOR)
    travel_days_frame.pack(pady=5)
    Label(travel_days_frame, text="Travel Days", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=15, anchor="w").pack(side="left", padx=5)
    entries['travel_days'] = Entry(travel_days_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    entries['travel_days'].pack(side="left", padx=5)

    create_button("Add Train", lambda: handle_add_train(entries)).pack(pady=20)
    create_back_button(manageSchedules).pack(pady=10)
    
def updateTrainPage():
    clear_root()
    heading = Label(root, text="Update Train", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=20)

    entries = {}
    
    # Train ID (required)
    train_id_frame = tk.Frame(root, bg=BG_COLOR)
    train_id_frame.pack(pady=5)
    Label(train_id_frame, text="Train ID*", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=15, anchor="w").pack(side="left", padx=5)
    entries['train_id'] = Entry(train_id_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    entries['train_id'].pack(side="left", padx=5)

    # Train Name (optional)
    train_name_frame = tk.Frame(root, bg=BG_COLOR)
    train_name_frame.pack(pady=5)
    Label(train_name_frame, text="Train Name", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=15, anchor="w").pack(side="left", padx=5)
    entries['train_name'] = Entry(train_name_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    entries['train_name'].pack(side="left", padx=5)

    # Other fields (all optional)

    optional_fields = [
        ('source_id', 'Source ID'),
        ('destination_id', 'Destination ID'),
        ('departure_time', 'Departure Time'),
        ('arrival_time', 'Arrival Time'),
        ('travel_days', 'Travel Days')
    ]
    
    for field_name, field_label in optional_fields:
        frame = tk.Frame(root, bg=BG_COLOR)
        frame.pack(pady=5)
        Label(frame, text=field_label, font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=15, anchor="w").pack(side="left", padx=5)
        entries[field_name] = Entry(frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
        entries[field_name].pack(side="left", padx=5)

    Label(root, text="* Required Fields", font=LABEL_FONT, bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=5)
    create_button("Update Train", lambda: handle_update_train(entries)).pack(pady=10)
    create_back_button(manageSchedules).pack(pady=10)

def deleteTrainPage():
    clear_root()
    heading = Label(root, text="Delete Train", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=40)

    train_id_frame = tk.Frame(root, bg=BG_COLOR)
    train_id_frame.pack(pady=10)
    Label(train_id_frame, text="Train ID", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left", padx=5)
    train_id_entry = Entry(train_id_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    train_id_entry.pack(side="left", padx=5)

    create_button("Delete Train", lambda: handle_delete_train(train_id_entry)).pack(pady=20)
    create_back_button(manageSchedules).pack(pady=10)
    
def manageStations():
    clear_root()
    heading = Label(root, text="Manage Stations", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=30)

    create_button("Add Station", addStationPage).pack(pady=10)
    create_button("View All Stations", display_stations).pack(pady=10)
    
    create_back_button(adminEntryPage).pack(pady=20)

def addStationPage():
    clear_root()
    heading = Label(root, text="Add New Station", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=40)

    station_name_frame = tk.Frame(root, bg=BG_COLOR)
    station_name_frame.pack(pady=10)
    Label(station_name_frame, text="Station Name", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left", padx=5)
    station_name_entry = Entry(station_name_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    station_name_entry.pack(side="left", padx=5)
    
    station_code_frame = tk.Frame(root, bg=BG_COLOR)
    station_code_frame.pack(pady=10)
    Label(station_code_frame, text="Station Code", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left", padx=5)
    station_code_entry = Entry(station_code_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    station_code_entry.pack(side="left", padx=5)

    create_button("Add Station", lambda: handle_add_station(station_name_entry, station_code_entry)).pack(pady=20)
    create_back_button(manageStations).pack(pady=10)

def searchTrain():
    clear_root()
    heading = Label(root, text="Search Trains", font=HEADING_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    heading.pack(pady=30)

    # Search by train number
    Label(root, text="Search by Train Number", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
    
    number_frame = tk.Frame(root, bg=BG_COLOR)
    number_frame.pack(pady=5)
    Label(number_frame, text="Train Number", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left", padx=5)
    train_no_entry = Entry(number_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    train_no_entry.pack(side="left", padx=5)
    
    create_button("Search by Number", lambda: handle_search_by_number(train_no_entry)).pack(pady=10)
    
    # Separator
    tk.Frame(root, height=2, width=400, bg=ACCENT_COLOR).pack(pady=20)
    
    # Search by location
    Label(root, text="Search by Location", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
    
    source_frame = tk.Frame(root, bg=BG_COLOR)
    source_frame.pack(pady=5)
    Label(source_frame, text="From", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left", padx=5)
    source_entry = Entry(source_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    source_entry.pack(side="left", padx=5)
    
    dest_frame = tk.Frame(root, bg=BG_COLOR)
    dest_frame.pack(pady=5)
    Label(dest_frame, text="To", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=12, anchor="w").pack(side="left", padx=5)
    dest_entry = Entry(dest_frame, width=ENTRY_WIDTH, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    dest_entry.pack(side="left", padx=5)
    
    create_button("Search by Location", lambda: handle_search_by_location(source_entry, dest_entry)).pack(pady=10)
    
    create_back_button(userEntryPage).pack(pady=20)

def add_passenger_row(parent_frame, passenger_num):
    # Create a frame for this passenger
    passenger_frame = tk.Frame(parent_frame, bg=BG_COLOR)
    passenger_frame.pack(pady=5, fill="x")

    # Passenger number
    Label(passenger_frame, text=f"Passenger {passenger_num}:", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR, width=12).pack(side="left", padx=5)

    # Name
    name_entry = Entry(passenger_frame, width=15, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    name_entry.pack(side="left", padx=5)
    name_entry.winfo_name = lambda: f"name_{passenger_num}"
    Label(passenger_frame, text="Age:", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(side="left")

    # Age
    age_entry = Entry(passenger_frame, width=5, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    age_entry.pack(side="left", padx=5)
    age_entry.winfo_name = lambda: f"age_{passenger_num}"
    Label(passenger_frame, text="Gender:", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(side="left")

    # Gender
    gender_entry = Entry(passenger_frame, width=8, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG)
    gender_entry.pack(side="left", padx=5)
    gender_entry.winfo_name = lambda: f"gender_{passenger_num}"
    
entryPage()
root.mainloop()

