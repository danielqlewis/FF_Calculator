import tkinter as tk
from tkinter import ttk


def create_result_display_frame(parent):
    # Create the labeled frame
    result_frame = ttk.LabelFrame(parent, text="Result", padding="10")

    # Create StringVar to hold the result
    result_text = tk.StringVar(value="")

    # Create the display label
    result_label = ttk.Label(result_frame,
                             textvariable=result_text,
                             font=('Arial', 10))
    result_label.grid(row=0, column=0, padx=10, pady=10)

    # Function to update the display
    def update_result(new_text):
        result_text.set(new_text)

    # Make the update function available to the caller
    result_frame.update_result = update_result

    return result_frame


# Test window
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Result Display Test")
    frame = create_result_display_frame(root)
    frame.grid(row=0, column=0, padx=10, pady=10)

    # Test updating the display
    frame.update_result("3x² + 2x + 1 mod 5")

    root.mainloop()