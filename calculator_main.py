# import tkinter as tk
# import field_selector_gui
# import poly_entry_gui
# import result_display_gui
# from tkinter import messagebox
# from irreducible_finder import find_irreducible
# from calculator_engine import FiniteFieldCalculator
#
#
# def set_frame_state(frame, state):
#     for child in frame.winfo_children():
#         try:
#             child.state(['disabled' if state else '!disabled'])
#         except:
#             # For widgets that don't have state method
#             child.configure(state='disabled' if state else 'normal')
#
#
# class CalculatorMain:
#     def __init__(self):
#         self.calculator = None
#         self.root = tk.Tk()
#         self.root.title("Finite Field Calculator")
#         self.frame0 = field_selector_gui.create_field_selection_frame(self.root, self.handle_field_change)
#         self.frame1 = poly_entry_gui.create_polynomial_operations_frame(self.root, 1)
#         self.frame2 = result_display_gui.create_result_display_frame(self.root)
#         self.frame0.grid(row=0, column=0, padx=10, pady=10)
#         self.frame1.grid(row=1, column=0, padx=10, pady=10)
#         self.frame2.grid(row=2, column=0, padx=10, pady=10)
#         set_frame_state(self.frame1, True)
#
#     def handle_field_change(self, p, n, is_active):
#         if is_active:
#             self.calculator = FiniteFieldCalculator(p, n)
#             self.frame0.update_modulus(str(self.calculator.polynomial_modulus))
#             self.frame1 = poly_entry_gui.create_polynomial_operations_frame(self.root, n, self.handle_calculation)
#             set_frame_state(self.frame1, False)  # Enable it
#             self.frame1.grid(row=1, column=0, padx=10, pady=10)
#         else:
#             self.calculator = None
#             self.frame2.update_result("")
#             self.frame1.destroy()
#             self.frame1 = poly_entry_gui.create_polynomial_operations_frame(self.root, 1)
#             set_frame_state(self.frame1, True)
#             self.frame1.grid(row=1, column=0, padx=10, pady=10)
#
#     def handle_calculation(self, coeffs1, coeffs2, operation):
#         if set(coeffs2) == {0}:
#             messagebox.showerror("Invalid Input", "Cannot divide by zero polynomial")
#         else:
#             result = self.calculator.handle_operation(coeffs1, coeffs2, operation)
#             self.frame2.update_result(str(result))
#
#
# if __name__ == "__main__":
#     active_calculator = CalculatorMain()
#     active_calculator.root.mainloop()

import tkinter as tk
from gui_coordinator import GuiCoordinator
from calculator_controller import CalculatorController

def main():
    root = tk.Tk()
    calculator_controller = CalculatorController()
    GuiCoordinator(root, calculator_controller)
    root.mainloop()


if __name__ == "__main__":
    main()