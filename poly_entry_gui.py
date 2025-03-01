from typing import List, Callable, Dict, Any


def create_polynomial_entry_row(frame, row_num: int, ttk, num_terms: int) -> List[Any]:
    entries: List[ttk.Entry] = []
    for i in range(1, 2 * num_terms + 1, 2):
        if i == 2 * num_terms - 3:
            text = "x + "
        else:
            if num_terms - i // 2 - 1 == 0:
                text = ""
            else:
                text = f"x^{num_terms - i // 2 - 1} + "
        ttk.Label(frame, text=text).grid(row=row_num, column=i, padx=5, pady=15)

    for i in range(0, 2 * num_terms, 2):
        entry = ttk.Entry(frame, width=5)
        entry.insert(0, "0")
        entry.grid(row=row_num, column=i, padx=5, pady=15)  # Increased pady
        entries.append(entry)

    return entries


def create_operation_buttons(frame, row_num: int, tk_packet: List[Any]):
    tk = tk_packet[0]
    ttk = tk_packet[1]
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


def create_polynomial_operations_frame(parent,
                                       on_calculation_requested: Callable[[List[int], List[int], str], None],
                                       tk_packet: List[Any],
                                       number_of_terms: int = 1
                                       ) -> Dict[str, Any]:
    tk = tk_packet[0]
    ttk = tk_packet[1]
    # Create the labeled frame
    poly_frame = ttk.LabelFrame(parent, text="Polynomial Operations", padding="10")

    # Create entry containers that we can update
    entries_container = ttk.Frame(poly_frame)
    entries_container.grid(row=0, column=0, sticky="nsew")

    # Initialize with empty lists
    entries1 = []
    entries2 = []
    operation_var = None
    calculate_button = None

    def setup_entry_widgets(num_terms: int) -> None:
        nonlocal entries1, entries2, operation_var, calculate_button

        # Clear existing widgets
        for widget in entries_container.winfo_children():
            widget.destroy()

        # Create two rows of polynomial entries
        entries1 = create_polynomial_entry_row(entries_container, 1, ttk, num_terms)
        operation_var = create_operation_buttons(entries_container, 2, [tk, ttk])
        entries2 = create_polynomial_entry_row(entries_container, 3, ttk, num_terms)

        calculate_button = ttk.Button(
            entries_container,
            text="Calculate",
            command=perform_calculation
        )
        calculate_button.grid(row=4, column=0, columnspan=14, pady=10)

    def perform_calculation() -> None:
        # Get values from entries
        poly1 = [int(entry.get()) for entry in reversed(entries1)]
        poly2 = [int(entry.get()) for entry in reversed(entries2)]
        operation = operation_var.get()

        # Call the callback
        on_calculation_requested(poly1, poly2, operation)

    def set_active(active: bool = True) -> None:
        state = ['!disabled'] if active else ['disabled']
        for entry in entries1 + entries2:
            entry.state(state)
        calculate_button.state(state)

    def update_field_size(num_terms: int) -> None:
        # Update the entries for the new field size
        setup_entry_widgets(num_terms)

    # Initial setup
    setup_entry_widgets(number_of_terms)

    # Start in disabled state until a field is selected
    set_active(False)

    # Return interface
    return {
        'frame': poly_frame,
        'set_active': set_active,
        'update_field_size': update_field_size
    }
