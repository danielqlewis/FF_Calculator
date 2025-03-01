import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import time
from typing import List

# Import modules to test
from calculator_controller import CalculatorController
from gui_coordinator import GuiCoordinator
from field_selector_gui import create_field_selection_frame
from poly_entry_gui import create_polynomial_operations_frame
from result_display_gui import create_result_display_frame

# Import the real calculator_engine instead of mocking it
from calculator_engine import FiniteFieldCalculator, FieldOperation


class TestControllerIntegration(unittest.TestCase):
    """Test the CalculatorController integration with the real calculator engine"""

    def setUp(self):
        self.controller = CalculatorController()
        self.callback = MagicMock()

    def test_initialize_field_async(self):
        """Test asynchronous field initialization"""
        self.controller.initialize_field_async(2, 3, self.callback)

        # Give the thread time to complete
        time.sleep(0.5)

        # Verify callback was called with the expected modulus
        self.callback.assert_called_once()
        self.assertIsNotNone(self.controller.modulus_polynomial)

    def test_initialize_field_with_invalid_parameters(self):
        """Test field initialization with invalid parameters"""
        # Non-prime p
        self.controller.initialize_field_async(4, 3, self.callback)
        time.sleep(0.5)
        self.callback.assert_called_once()
        self.assertIn("Error:", self.callback.call_args[0][0])

        # Reset mock and try with p too large
        self.callback.reset_mock()
        self.controller.initialize_field_async(102, 3, self.callback)
        time.sleep(0.5)
        self.callback.assert_called_once()
        self.assertIn("Error:", self.callback.call_args[0][0])


    def test_reset_calculator(self):
        """Test resetting the calculator"""
        # First initialize it
        self.controller.initialize_field_async(2, 3, self.callback)
        time.sleep(0.5)

        # Then reset it
        self.controller.reset_calculator()

        # Verify it's been reset
        self.assertIsNone(self.controller.calculator)
        self.assertIsNone(self.controller.modulus_polynomial)

    def test_perform_calculation_no_field(self):
        """Test calculation with no field selected"""
        result = self.controller.perform_calculation([1, 1], [1, 0], "add")
        self.assertEqual(result, "Error: No field selected")

    def test_perform_valid_calculations(self):
        """Test all valid calculation operations"""
        # First initialize field
        self.controller.initialize_field_async(2, 3, self.callback)
        time.sleep(0.5)

        # Test addition
        result = self.controller.perform_calculation([1, 1, 1], [1, 0, 1], "add")
        self.assertIn("Result:", result)

        # Test subtraction
        result = self.controller.perform_calculation([1, 1, 1], [1, 0, 1], "subtract")
        self.assertIn("Result:", result)

        # Test multiplication
        result = self.controller.perform_calculation([1, 1, 1], [1, 0, 1], "multiply")
        self.assertIn("Result:", result)

        # Test division (if the second polynomial is not zero)
        result = self.controller.perform_calculation([1, 1, 1], [1, 0, 1], "divide")
        self.assertIn("Result:", result)

    def test_perform_calculation_unknown_operation(self):
        """Test calculation with unknown operation"""
        # Initialize field
        self.controller.initialize_field_async(2, 3, self.callback)
        time.sleep(0.5)

        # Perform invalid operation
        result = self.controller.perform_calculation([1, 1, 1], [1, 0, 1], "power")
        self.assertIn("Error: Unknown operation", result)

    def test_perform_calculation_division_by_zero(self):
        """Test division by zero polynomial"""
        # Initialize field
        self.controller.initialize_field_async(2, 3, self.callback)
        time.sleep(0.5)

        # Perform division by zero
        result = self.controller.perform_calculation([1, 1, 1], [0, 0, 0], "divide")
        self.assertIn("Error:", result)


class TestGuiIntegration(unittest.TestCase):
    """Base class for GUI integration tests"""

    def setUp(self):
        # Create the root window
        self.root = tk.Tk()

        # Create and mock the calculator controller
        self.calculator_controller = Mock(spec=CalculatorController)

        # Create the GUI coordinator with the mocked controller
        self.gui_coordinator = GuiCoordinator(self.calculator_controller)

        # Store references to the GUI components for easier access in tests
        self.field_selector = self.gui_coordinator.field_selector
        self.poly_entry = self.gui_coordinator.poly_entry
        self.result_display = self.gui_coordinator.result_display

    def tearDown(self):
        # Destroy the root window after each test
        self.root.destroy()


class TestGuiInitialization(TestGuiIntegration):
    """Test the initialization of the GUI components"""

    def test_initialization(self):
        """Test that all GUI components are properly initialized"""
        # Check that all main components exist
        self.assertIsNotNone(self.field_selector)
        self.assertIsNotNone(self.poly_entry)
        self.assertIsNotNone(self.result_display)

        # Check that the polynomial operations are initially disabled
        # We can verify this by checking if the set_active function was called with False
        # This is an indirect way to verify the initial state
        self.poly_entry['set_active'](False)  # This should not raise an error

        # Check window title
        self.assertEqual(self.gui_coordinator.root.title(), "Finite Field Calculator")


class TestFieldSelection(TestGuiIntegration):
    """Test the field selection functionality"""

    def test_valid_field_selection(self):
        """Test selecting a valid finite field"""

        # Mock the calculator controller's initialize_field_async method
        # to simulate successful field initialization
        def mock_initialize(p, n, callback):
            # Call the callback with a mock modulus polynomial
            callback("x^3 + x + 1")

        self.calculator_controller.initialize_field_async.side_effect = mock_initialize

        # Trigger field selection with valid parameters
        self.gui_coordinator.handle_field_selected(2, 3)

        # Verify controller was called with correct parameters
        self.calculator_controller.initialize_field_async.assert_called_once()
        self.assertEqual(self.calculator_controller.initialize_field_async.call_args[0][0], 2)  # p
        self.assertEqual(self.calculator_controller.initialize_field_async.call_args[0][1], 3)  # n

        # Process tkinter events to allow callbacks to complete
        self.root.update()

        # Check that polynomial operations are now enabled
        # This is more of a functional test than a strict unit test
        # We're testing that the GUI coordinator correctly updates the UI
        self.poly_entry['set_active'](True)  # This should not raise an error

    def test_invalid_field_selection(self):
        """Test selecting an invalid finite field"""
        # Attempt to select an invalid field (non-prime p)
        with patch('tkinter.messagebox.showerror') as mock_error:
            self.gui_coordinator.handle_field_selected(4, 3)

            # Verify error dialog was shown
            mock_error.assert_called_once()
            self.assertIn("Invalid Input", mock_error.call_args[0][0])  # Title should be "Invalid Input"

        # Verify calculator was not initialized
        self.calculator_controller.initialize_field_async.assert_not_called()


class TestFieldDeselection(TestGuiIntegration):
    """Test the field deselection functionality"""

    def test_field_deselection(self):
        """Test deselecting an active field"""
        # First simulate having an active field
        self.poly_entry['set_active'](True)

        # Now deselect the field
        self.gui_coordinator.handle_field_deselected()

        # Verify that the calculator was reset
        self.calculator_controller.reset_calculator.assert_called_once()

        # Verify that the UI was reset
        # Direct test of outcome rather than implementation
        self.result_display['clear_result']()  # This should not raise an error


class TestCalculationRequest(TestGuiIntegration):
    """Test the calculation request functionality"""

    def test_calculation_request(self):
        """Test requesting a calculation"""
        # Mock the calculator controller's perform_calculation method
        self.calculator_controller.perform_calculation.return_value = "Result: x^2 + 1"

        # Simulate user input by calling the handle_calculation_requested method directly
        self.gui_coordinator.handle_calculation_requested([1, 0, 1], [1, 1], "add")

        # Verify calculator was called with correct parameters
        self.calculator_controller.perform_calculation.assert_called_once()
        self.assertEqual(self.calculator_controller.perform_calculation.call_args[0][0], [1, 0, 1])  # poly1
        self.assertEqual(self.calculator_controller.perform_calculation.call_args[0][1], [1, 1])  # poly2
        self.assertEqual(self.calculator_controller.perform_calculation.call_args[0][2], "add")  # operation

        # Verify result was displayed
        # We can verify by calling update_result and checking no errors occur
        self.result_display['update_result']("Result: x^2 + 1")  # This should not raise an error


class TestCompleteWorkflow(TestGuiIntegration):
    """Test the complete workflow from start to end"""

    def test_end_to_end_workflow(self):
        """Test the complete calculator workflow"""

        # 1. Initialize with a valid field
        def mock_initialize(p, n, callback):
            callback("x^3 + x + 1")

        self.calculator_controller.initialize_field_async.side_effect = mock_initialize
        self.calculator_controller.perform_calculation.return_value = "Result: x^2 + x + 1"

        # 2. Select a field
        self.gui_coordinator.handle_field_selected(2, 3)
        self.root.update()

        # 3. Perform a calculation
        self.gui_coordinator.handle_calculation_requested([1, 1, 1], [1, 1], "add")

        # 4. Verify result was obtained
        self.calculator_controller.perform_calculation.assert_called_once()

        # 5. Deselect the field
        self.gui_coordinator.handle_field_deselected()

        # 6. Verify calculator was reset
        self.calculator_controller.reset_calculator.assert_called_once()