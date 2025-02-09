import tkinter as tk
from tkinter import ttk


def create_polynomial_entry_row(frame, row_num, num_terms):
    """Create a row of entry boxes for polynomial coefficients with connecting labels.

    Args:
        frame: The tkinter frame to place the entries in
        row_num: Which row to place this polynomial entry on
        num_terms: Number of terms in the polynomial

    Returns:
        List of entry widgets for accessing the values later
    """
    entries = []
    for i in range(1, 2 * num_terms + 1, 2):
        if i == 2 * num_terms - 3:
            text = "x + "
        else:
            if num_terms - i // 2 - 1 == 0:
                text = ""
            else:
                text = f"x^{num_terms - i // 2 - 1} + "
        ttk.Label(frame, text=text).grid(row=row_num, column=i, padx=5, pady=15)  # Increased pady

    for i in range(0, 2 * num_terms, 2):
        entry = ttk.Entry(frame, width=5)
        entry.insert(0, "0")
        entry.grid(row=row_num, column=i, padx=5, pady=15)  # Increased pady
        entries.append(entry)

    return entries


def create_operation_buttons(frame, row_num):
    # Create a variable to track which operation is selected
    operation_var = tk.StringVar(value="add")

    # Create a frame just for the radio buttons to help with centering
    button_frame = ttk.Frame(frame)
    button_frame.grid(row=row_num, column=0, columnspan=14, pady=20)

    # Style for larger text
    style = ttk.Style()
    style.configure('Big.TRadiobutton', font=('Arial', 12, 'bold'))

    ttk.Radiobutton(button_frame,
                    text="+",
                    variable=operation_var,
                    style='Big.TRadiobutton',
                    value="add").grid(row=0, column=0, padx=20)

    ttk.Radiobutton(button_frame,
                    text="-",
                    variable=operation_var,
                    style='Big.TRadiobutton',
                    value="subtract").grid(row=0, column=1, padx=20)

    ttk.Radiobutton(button_frame,
                    text="×",
                    variable=operation_var,
                    style='Big.TRadiobutton',
                    value="multiply").grid(row=0, column=2, padx=20)

    ttk.Radiobutton(button_frame,
                    text="÷",
                    variable=operation_var,
                    style='Big.TRadiobutton',
                    value="divide").grid(row=0, column=3, padx=20)

    return operation_var


def perform_calculation(entries1, entries2, operation_var):
    coeffs1 = [int(entry.get()) for entry in reversed(entries1)]
    coeffs2 = [int(entry.get()) for entry in reversed(entries2)]
    operation = operation_var.get()

    # For now, just print to verify we're getting the right info
    print(f"Polynomial 1 coefficients: {coeffs1}")
    print(f"Polynomial 2 coefficients: {coeffs2}")
    print(f"Operation selected: {operation}")


def create_polynomial_operations_frame(parent, number_of_terms=1):
    """Create a frame containing the polynomial operation interface.

    Args:
        parent: The parent widget to place this frame in
        number_of_terms: Number of terms in the polynomials (default 12)

    Returns:
        A labeled frame containing the polynomial entry and operation interface
    """
    # Create the labeled frame
    poly_frame = ttk.LabelFrame(parent, text="Polynomial Operations", padding="10")

    # Create two rows of polynomial entries
    entries1 = create_polynomial_entry_row(poly_frame, 1, number_of_terms)
    operation_var = create_operation_buttons(poly_frame, 2)
    entries2 = create_polynomial_entry_row(poly_frame, 3, number_of_terms)

    calculate_button = ttk.Button(
        poly_frame,
        text="Calculate",
        command=lambda: perform_calculation(entries1, entries2, operation_var)
    )
    calculate_button.grid(row=4, column=0, columnspan=14, pady=10)

    return poly_frame


# Test window
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Polynomial Operations Test")
    frame = create_polynomial_operations_frame(root, 5)
    frame.grid(row=0, column=0, padx=10, pady=10)
    root.mainloop()