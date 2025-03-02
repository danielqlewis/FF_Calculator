import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List


from field_selector_gui import create_field_selection_frame
from poly_entry_gui import create_polynomial_operations_frame
from result_display_gui import create_result_display_frame


def is_prime(n: int) -> bool:
    """
    Check if a number is prime using trial division.

    Args:
        n: The number to check.

    Returns:
        True if n is prime, False otherwise.
    """
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


class GuiCoordinator:
    """
    Main coordinator for the Finite Field Calculator GUI.

    Manages the interactions between UI components and orchestrates
    the communication between frontend and backend (CalculatorController).
    """

    def __init__(self, calculator_controller):
        """
        Initialize the GUI coordinator with a calculator controller.

        Args:
            calculator_controller: Controller instance that handles the mathematical operations
                                  and manages the FiniteFieldCalculator.
        """
        self.root = tk.Tk()
        self.calculator_controller = calculator_controller

        # GUI component containers
        self.field_selector: Dict[str, Any] = {}
        self.poly_entry: Dict[str, Any] = {}
        self.result_display: Dict[str, Any] = {}

        self.root.title("Finite Field Calculator")
        self.root.geometry("800x600")

        self._init_ui()

    def adjust_window_size(self) -> None:
        """
        Adjust the window size to fit the content.

        Recalculates the required dimensions based on the current content
        and resizes the window accordingly.
        """
        self.root.update_idletasks()

        width = self.root.winfo_reqwidth() + 20
        height = self.root.winfo_reqheight() + 20

        self.root.geometry(f"{width}x{height}")

    def _init_ui(self) -> None:
        """
        Initialize all UI components and lay them out in the main window.

        Creates the field selector, polynomial entry, and result display components
        and arranges them vertically in the main frame.
        """
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.field_selector = create_field_selection_frame(
            main_frame,
            on_field_select=self.handle_field_selected,
            on_field_deselect=self.handle_field_deselected,
            tk_packet=[tk, ttk]
        )
        self.field_selector['frame'].pack(fill=tk.X, pady=10)

        self.poly_entry = create_polynomial_operations_frame(
            main_frame,
            on_calculation_requested=self.handle_calculation_requested,
            tk_packet=[tk, ttk],
            number_of_terms=1  # Default size until field is selected
        )
        self.poly_entry['frame'].pack(fill=tk.X, pady=10)

        self.result_display = create_result_display_frame(main_frame, [tk, ttk])
        self.result_display['frame'].pack(fill=tk.X, pady=10)

        self.adjust_window_size()

    def _update_ui_after_field_initialized(self, modulus: str, n: int) -> None:
        """
        Update UI components after field initialization is complete.

        Args:
            modulus: String representation of the field modulus.
            n: Degree of the field extension.
        """
        self.field_selector['update_modulus_display'](f"Field modulus: {modulus}")
        self.poly_entry['update_field_size'](n)
        self.poly_entry['set_active'](True)
        self.adjust_window_size()

    def handle_field_selected(self, p: int, n: int) -> None:
        """
        Handle user selection of field parameters.

        Validates inputs, shows loading state, and initiates asynchronous
        field initialization in the calculator controller.

        Args:
            p: The prime characteristic of the base field.
            n: The degree of the field extension.
        """
        try:
            # Validate inputs
            if not (1 < p <= 101):
                raise ValueError("Must have 1 < p < 102")
            if not (0 < n <= 12):
                raise ValueError("Must have 0 < n < 13")
            if not is_prime(p):
                raise ValueError("p must be prime")

            # Show loading state
            self.field_selector['deactivate_and_show_loading']()

            # Define callback for when field initialization completes
            def on_field_initialized(modulus: str) -> None:
                # This will be called from a background thread, so we need to
                # schedule the UI updates on the main thread
                self.root.after(0, lambda: self._update_ui_after_field_initialized(modulus, n))

            # Start the asynchronous initialization
            self.calculator_controller.initialize_field_async(p, n, on_field_initialized)

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            self.field_selector['reset_to_initial_state']()
            return

    def handle_field_deselected(self) -> None:
        """
        Handle user deselection of the current field.

        Resets the UI to its initial state and clears the calculator.
        """
        self.field_selector['reset_to_initial_state']()
        self.calculator_controller.reset_calculator()
        self.poly_entry['update_field_size'](1)
        self.poly_entry['set_active'](False)
        self.result_display['clear_result']()
        self.adjust_window_size()

    def handle_calculation_requested(self, poly1: List[int], poly2: List[int], operation: str) -> None:
        """
        Handle calculation request from the polynomial entry component.

        Delegates the calculation to the controller and updates the result display.

        Args:
            poly1: Coefficients of the first polynomial.
            poly2: Coefficients of the second polynomial.
            operation: String identifier of the operation to perform.
        """
        result = self.calculator_controller.perform_calculation(poly1, poly2, operation)
        self.result_display['update_result'](result)
