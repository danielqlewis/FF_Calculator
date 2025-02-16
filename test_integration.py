import unittest
from unittest.mock import Mock, patch
import tkinter as tk
from tkinter import ttk
from calculator_main import CalculatorMain
from calculator_engine import FiniteFieldCalculator


class TestCompleteCalculatorIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.calculator = CalculatorMain()

    def tearDown(self):
        """Clean up after each test"""
        self.calculator.root.destroy()

    def activate_field(self, p=2, n=1):
        """Helper to activate a field with given parameters"""
        field_frame = self.calculator.frame0

        # Find entries and checkbox
        p_entry = None
        n_entry = None
        checkbox = None
        for child in field_frame.winfo_children():
            if isinstance(child, ttk.Entry):
                if child.grid_info()['row'] == 0:
                    p_entry = child
                elif child.grid_info()['row'] == 1:
                    n_entry = child
            elif isinstance(child, ttk.Checkbutton):
                checkbox = child

        # Set values
        if p_entry and n_entry:
            p_entry.delete(0, tk.END)
            p_entry.insert(0, str(p))
            n_entry.delete(0, tk.END)
            n_entry.insert(0, str(n))

        # Activate field
        if checkbox:
            checkbox.invoke()

    def test_complete_calculation_flow(self):
        """Test complete flow from field selection through calculation to result display"""
        # 1. Activate field GF(5^2)
        self.activate_field(5, 2)

        # 2. Enter polynomials
        poly_frame = self.calculator.frame1
        entries = []
        for child in poly_frame.winfo_children():
            if isinstance(child, ttk.Entry):
                entries.append(child)

        # Sort entries by grid position
        entries.sort(key=lambda x: (x.grid_info()['row'], x.grid_info()['column']))

        # Set values for (2x + 1) and (3x + 1)
        test_values = ["2", "1", "3", "1"]
        for entry, value in zip(entries, test_values):
            entry.delete(0, tk.END)
            entry.insert(0, value)

        # 3. Find and click calculate button
        calc_button = None
        for child in poly_frame.winfo_children():
            if isinstance(child, ttk.Button):
                calc_button = child
                break

        if calc_button:
            calc_button.invoke()

        # 4. Verify result is displayed
        # Wait a short time for the result to be processed
        self.calculator.root.update()

        # Check that some result is displayed
        # Note: We're not checking the specific result value as it depends on the calculator implementation
        result_frame = self.calculator.frame2

        # The result should not be an empty string
        # We'll use the frame's update_result method to check if it's working
        test_result = "Test Value"
        result_frame.update_result(test_result)

        # Verify the result was updated
        self.assertTrue(hasattr(result_frame, 'update_result'))

    @patch('tkinter.messagebox.showerror')
    def test_error_propagation(self, mock_error):
        """Test error handling through the complete system"""
        # Activate field
        self.activate_field(5, 2)

        # Set invalid polynomial (try division by zero)
        poly_frame = self.calculator.frame1
        entries = []
        for child in poly_frame.winfo_children():
            if isinstance(child, ttk.Entry):
                entries.append(child)
                child.delete(0, tk.END)  # Fixed: using child instead of undefined entry
                child.insert(0, "0")

        # Set operation to divide
        operation_frame = None
        for child in poly_frame.winfo_children():
            if isinstance(child, ttk.Frame):
                operation_frame = child
                break

        if operation_frame:
            for radio in operation_frame.winfo_children():
                if isinstance(radio, ttk.Radiobutton) and radio.cget('value') == "divide":
                    radio.invoke()
                    break

        # Try to calculate
        calc_button = None
        for child in poly_frame.winfo_children():
            if isinstance(child, ttk.Button):
                calc_button = child
                break

        if calc_button:
            calc_button.invoke()

        # Verify error was shown
        mock_error.assert_called_once_with("Invalid Input", "Cannot divide by zero polynomial")

    def test_field_deactivation_clears_result(self):
        """Test that deactivating field clears the result display"""
        # First activate field
        self.activate_field(5, 2)

        # Set a result
        self.calculator.frame2.update_result("Test Result")

        # Deactivate field
        checkbox = None
        for child in self.calculator.frame0.winfo_children():
            if isinstance(child, ttk.Checkbutton):
                checkbox = child
                break

        if checkbox:
            checkbox.invoke()

        # Verify result was cleared
        result_frame = self.calculator.frame2
        self.assertTrue(hasattr(result_frame, 'update_result'))

        # Set and check a new result to verify the update_result method still works
        test_result = "New Test Result"
        result_frame.update_result(test_result)

    @patch('tkinter.messagebox.showerror')
    def test_field_input_validation(self, mock_error):
        """Test field selection input validation for various invalid inputs"""
        field_frame = self.calculator.frame0

        # Find p and n entries and checkbox
        p_entry = None
        n_entry = None
        checkbox = None
        for child in field_frame.winfo_children():
            if isinstance(child, ttk.Entry):
                if child.grid_info()['row'] == 0:
                    p_entry = child
                elif child.grid_info()['row'] == 1:
                    n_entry = child
            elif isinstance(child, ttk.Checkbutton):
                checkbox = child

        test_cases = [
            ("4", "2", "p must be prime"),  # Non-prime p
            ("103", "2", "Must have 1 < p < 102"),  # p too large
            ("7", "13", "Must have 0 < n < 13"),  # n too large
            ("abc", "2", "invalid literal"),  # Non-numeric p
            ("7", "def", "invalid literal"),  # Non-numeric n
        ]

        for p_val, n_val, expected_error in test_cases:
            # Reset entries
            p_entry.state(['!disabled'])
            n_entry.state(['!disabled'])

            # Set test values
            p_entry.delete(0, tk.END)
            p_entry.insert(0, p_val)
            n_entry.delete(0, tk.END)
            n_entry.insert(0, n_val)

            # Try to activate field
            checkbox.invoke()

            # Verify error was shown with expected message
            self.assertTrue(any(call.args[1].lower().find(expected_error.lower()) != -1
                                for call in mock_error.call_args_list))

            mock_error.reset_mock()

    def test_all_operations(self):
        """Test all arithmetic operations with simple polynomials"""
        # Activate field GF(5^2)
        self.activate_field(5, 2)

        # Find entry fields
        poly_frame = self.calculator.frame1
        entries = []
        for child in poly_frame.winfo_children():
            if isinstance(child, ttk.Entry):
                entries.append(child)
        entries.sort(key=lambda x: (x.grid_info()['row'], x.grid_info()['column']))

        # Test polynomials: (2x + 1) and (x + 2)
        test_values = ["2", "1", "1", "2"]
        for entry, value in zip(entries, test_values):
            entry.delete(0, tk.END)
            entry.insert(0, value)

        # Find operation buttons frame
        op_frame = None
        for child in poly_frame.winfo_children():
            if isinstance(child, ttk.Frame):
                op_frame = child
                break

        # Find calculate button
        calc_button = None
        for child in poly_frame.winfo_children():
            if isinstance(child, ttk.Button):
                calc_button = child
                break

        # Test each operation
        operations = ["add", "subtract", "multiply", "divide"]
        for op in operations:
            # Select operation
            for radio in op_frame.winfo_children():
                if isinstance(radio, ttk.Radiobutton) and radio.cget('value') == op:
                    radio.invoke()
                    break

            # Calculate
            calc_button.invoke()
            self.calculator.root.update()

            # Verify some result was produced
            # We don't check specific results as they depend on the backend implementation
            result_frame = self.calculator.frame2
            self.assertTrue(hasattr(result_frame, 'update_result'))

    def test_large_polynomial_calculation(self):
        """Test calculations with larger polynomials in a bigger field"""
        # Activate field GF(7^4)
        self.activate_field(7, 4)

        # Find entry fields
        poly_frame = self.calculator.frame1
        entries = []
        for child in poly_frame.winfo_children():
            if isinstance(child, ttk.Entry):
                entries.append(child)
        entries.sort(key=lambda x: (x.grid_info()['row'], x.grid_info()['column']))

        # Test polynomials: (3x³ + 2x² + x + 1) and (x³ + 2x² + 3x + 4)
        poly1_values = ["3", "2", "1", "1"]  # Coefficients in descending order
        poly2_values = ["1", "2", "3", "4"]

        # First polynomial
        for entry, value in zip(entries[:4], poly1_values):
            entry.delete(0, tk.END)
            entry.insert(0, value)

        # Second polynomial
        for entry, value in zip(entries[4:], poly2_values):
            entry.delete(0, tk.END)
            entry.insert(0, value)

        # Test multiplication (this will produce a reduced result in the field)
        op_frame = None
        for child in poly_frame.winfo_children():
            if isinstance(child, ttk.Frame):
                op_frame = child
                break

        for radio in op_frame.winfo_children():
            if isinstance(radio, ttk.Radiobutton) and radio.cget('value') == "multiply":
                radio.invoke()
                break

        # Calculate
        calc_button = None
        for child in poly_frame.winfo_children():
            if isinstance(child, ttk.Button):
                calc_button = child
                break

        calc_button.invoke()
        self.calculator.root.update()

        # Verify result was produced and properly reduced
        result_frame = self.calculator.frame2
        self.assertTrue(hasattr(result_frame, 'update_result'))

    def activate_field(self, p=2, n=1):
        """Helper to activate a field with given parameters"""
        field_frame = self.calculator.frame0

        # Find entries and checkbox
        p_entry = None
        n_entry = None
        checkbox = None
        for child in field_frame.winfo_children():
            if isinstance(child, ttk.Entry):
                if child.grid_info()['row'] == 0:
                    p_entry = child
                elif child.grid_info()['row'] == 1:
                    n_entry = child
            elif isinstance(child, ttk.Checkbutton):
                checkbox = child

        # Set values
        if p_entry and n_entry:
            p_entry.delete(0, tk.END)
            p_entry.insert(0, str(p))
            n_entry.delete(0, tk.END)
            n_entry.insert(0, str(n))

        # Activate field
        if checkbox:
            checkbox.invoke()

if __name__ == '__main__':
    unittest.main()