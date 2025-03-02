from typing import Callable, Dict, List, Any


def create_field_selection_frame(parent,
                                 on_field_select: Callable[[int, int], None],
                                 on_field_deselect: Callable[[], None],
                                 tk_packet: List[Any]
                                 ) -> Dict[str, Any]:
    """
    Create a frame for selecting the field parameters p and n for GF(p^n).

    Args:
        parent: The parent widget to contain this frame.
        on_field_select: Callback function triggered when a field is selected.
                        Takes p and n as integer arguments.
        on_field_deselect: Callback function triggered when a field is deselected.
        tk_packet: A list containing the tkinter and ttk modules.

    Returns:
        A dictionary containing the frame widget and interface functions:
        - 'frame': The created frame widget
        - 'deactivate_and_show_loading': Function to disable inputs and show loading state
        - 'update_modulus_display': Function to update the modulus display text
        - 'reset_to_initial_state': Function to reset the UI to its initial state
    """
    tk = tk_packet[0]
    ttk = tk_packet[1]
    # Create the labeled frame
    field_frame = ttk.LabelFrame(parent, text="Field Selection", padding="10")

    # Create a StringVar for our polynomial modulus label
    mod_text = tk.StringVar(value="")

    mod_label = ttk.Label(field_frame, textvariable=mod_text, font=('Arial', 8, 'italic'))
    mod_label.grid(row=4, column=0, sticky='ne', padx=5)

    # Add prompt and warning labels
    ttk.Label(field_frame,
              text="Select finite field GF(p^n)",
              font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=2, pady=5)

    ttk.Label(field_frame,
              text="must have p ≤ 101 and n ≤ 12",
              font=('Arial', 8)).grid(row=1, column=0, columnspan=2, pady=5)

    # Create p entry with label
    ttk.Label(field_frame, text="p:").grid(row=0, column=2, padx=5, pady=5)
    p_entry = ttk.Entry(field_frame, width=5)
    p_entry.insert(0, "2")
    p_entry.grid(row=0, column=3, padx=5, pady=5)

    # Create n entry with label
    ttk.Label(field_frame, text="n:").grid(row=1, column=2, padx=5, pady=5)
    n_entry = ttk.Entry(field_frame, width=5)
    n_entry.insert(0, "1")
    n_entry.grid(row=1, column=3, padx=5, pady=5)

    # Variable to track active state
    is_active = tk.BooleanVar(value=False)

    def toggle_field() -> None:
        """
        Handle toggling of the active field checkbox.

        Calls the appropriate callback based on the new state of the checkbox.
        """
        current_state = is_active.get()

        if current_state:  # Checkbox was just checked
            p = int(p_entry.get())
            n = int(n_entry.get())
            on_field_select(p, n)
        else:  # Checkbox was just unchecked
            on_field_deselect()

    # Create the toggle switch
    active_check = ttk.Checkbutton(field_frame,
                                   text="Set Active Field",
                                   variable=is_active,
                                   command=toggle_field)
    active_check.grid(row=3, column=0, columnspan=2, pady=10)

    # Functions for coordinator to call
    def deactivate_and_show_loading() -> None:
        """
        Disable input elements and display loading message.
        Called when field initialization begins.
        """
        p_entry.state(['disabled'])
        n_entry.state(['disabled'])
        active_check.state(['disabled'])
        mod_text.set("Finding irreducible modulus...")

    def update_modulus_display(modulus_text: str) -> None:
        """
        Update the display with the calculated irreducible polynomial.

        Args:
            modulus_text: Text describing the irreducible polynomial.
        """
        mod_text.set(modulus_text)
        active_check.state(['!disabled'])

    def reset_to_initial_state() -> None:
        """
        Reset the UI components to their initial state.
        Called when deselecting a field or after an error.
        """
        is_active.set(False)
        p_entry.state(['!disabled'])
        n_entry.state(['!disabled'])
        active_check.state(['!disabled'])
        mod_text.set("")

    # Return the frame and interface functions
    return {
        'frame': field_frame,
        'deactivate_and_show_loading': deactivate_and_show_loading,
        'update_modulus_display': update_modulus_display,
        'reset_to_initial_state': reset_to_initial_state
    }
