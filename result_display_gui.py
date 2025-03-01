from typing import Dict, List, Any, Callable


def create_result_display_frame(parent, tk_packet: List[Any]
                                ) -> Dict[str, Any]:
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
        result_text.set(new_text)

    def clear_result() -> None:
        result_text.set("")

    return {
        'frame': result_frame,
        'update_result': update_result,
        'clear_result': clear_result
    }
