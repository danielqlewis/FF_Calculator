from typing import Dict, List, Any, Callable


def create_result_display_frame(parent, tk_packet: List[Any]
                                ) -> Dict[str, Any]:
    """
    Create a frame for displaying calculation results.

    Args:
        parent: The parent widget to contain this frame.
        tk_packet: A list containing the tkinter and ttk modules.

    Returns:
        A dictionary containing the frame widget and interface functions:
        - 'frame': The created frame widget
        - 'update_result': Function to update the displayed result text
        - 'clear_result': Function to clear the displayed result
    """
    tk = tk_packet[0]
    ttk = tk_packet[1]
    # Create the labeled frame
    result_frame = ttk.LabelFrame(parent, text="Result", padding="10")

    # Create StringVar to hold the result
    result_text = tk.StringVar(value="")

    # Create the display label
    result_label = ttk.Label(result_frame,
                             textvariable=result_text,
                             font=('Arial', 10))
    result_label.grid(row=0, column=0, padx=10, pady=10)

    def update_result(new_text: str) -> None:
        """
        Update the displayed result text.

        Args:
            new_text: The new text to display.
        """
        result_text.set(new_text)

    def clear_result() -> None:
        """
        Clear the displayed result text.
        """
        result_text.set("")

    return {
        'frame': result_frame,
        'update_result': update_result,
        'clear_result': clear_result
    }
