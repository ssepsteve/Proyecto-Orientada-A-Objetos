import tkinter as tk

class DateEntryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Date Entry Format")

        self.date_entry = tk.Entry(root, width=10)
        self.date_entry.pack(pady=20)

        # Bind the key release event to the format function
        self.date_entry.bind("<KeyRelease>", self.format_date)

    def format_date(self, event):
        # Get the current input
        input_text = self.date_entry.get()

        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, input_text))

        # Format the digits into YYYY-MM-DD
        formatted_date = ''
        if len(digits) >= 4:
            formatted_date += digits[:4]  # Year
            if len(digits) >= 6:
                formatted_date += '-' + digits[4:6]  # Month
                if len(digits) >= 8:
                    formatted_date += '-' + digits[6:8]  # Day

        # Update the entry with the formatted date
        self.date_entry.after(1, lambda: self.update_entry(formatted_date))

    def update_entry(self, formatted_date):
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, formatted_date)

        # Move the cursor to the end of the entry
        self.date_entry.icursor(len(formatted_date))

if __name__ == "__main__":
    root = tk.Tk()
    app = DateEntryApp(root)
    root.mainloop()