import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from field_selector_gui import create_field_selection_frame
from poly_entry_gui import create_polynomial_operations_frame
from result_display_gui import create_result_display_frame


def is_prime(n):
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


class GuiCoordinator:
    def __init__(self, root, calculator_controller):
        self.root = root
        self.calculator_controller = calculator_controller

        root.title("Finite Field Calculator")
        root.geometry("800x600")

        self._init_ui()

    def _init_ui(self):
        """Initialize all UI components and layout"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.field_selector = create_field_selection_frame(
            main_frame,
            on_field_select=self.handle_field_selected,
            on_field_deselect=self.handle_field_deselected
        )
        self.field_selector['frame'].pack(fill=tk.X, pady=10)

        self.poly_entry = create_polynomial_operations_frame(
            main_frame,
            on_calculation_requested=self.handle_calculation_requested,
            number_of_terms=1  # Default size until field is selected
        )
        self.poly_entry['frame'].pack(fill=tk.X, pady=10)

        self.result_display = create_result_display_frame(main_frame)
        self.result_display['frame'].pack(fill=tk.X, pady=10)

    # ===== Field Selector Callbacks =====
    def handle_field_selected(self, p, n):
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
            modulus = self.calculator_controller.initialize_field(p, n)
            # Update the UI with the found modulus
            self.field_selector['update_modulus_display'](f"Field modulus: {modulus}")

            self.poly_entry['update_field_size'](n)
            self.poly_entry['set_active'](True)

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            self.field_selector['reset_to_initial_state']()
            return

    def handle_field_deselected(self):
        self.field_selector['reset_to_initial_state']()
        self.calculator_controller.reset_calculator()
        self.poly_entry['update_field_size'](1)
        self.poly_entry['set_active'](False)
        self.result_display['clear_result']()

    def handle_calculation_requested(self, poly1, poly2, operation):
        result = self.calculator_controller.perform_calculation(poly1, poly2, operation)
        self.result_display['update_result'](result)
