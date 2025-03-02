from threading import Thread
from typing import List, Callable

from calculator_engine import FiniteFieldCalculator, FieldOperation


class CalculatorController:
    """
    Controller class that mediates between the GUI and the finite field calculator.

    Handles asynchronous initialization of finite fields and performs calculations
    requested by the GUI using the underlying FiniteFieldCalculator.
    """

    def __init__(self):
        """
        Initialize a new calculator controller.

        The calculator instance and modulus polynomial are initially set to None
        until a field is initialized.
        """
        self._calculator = None
        self._modulus_polynomial = None

    def initialize_field_async(self, p: int, n: int, on_complete: Callable[[str], None]) -> None:
        """
        Initialize a finite field GF(p^n) asynchronously in a background thread.

        Args:
            p: The prime characteristic of the base field.
            n: The degree of the field extension.
            on_complete: Callback function to be called when initialization completes.
                        Takes a string parameter with the result (modulus polynomial or error message).
        """
        def _initialize() -> None:
            """
            Internal function to perform the actual initialization in a background thread.
            Calls the on_complete callback with the result or error message.
            """
            try:
                calculator = FiniteFieldCalculator(p, n)
                modulus_string = str(calculator.polynomial_modulus)

                # Store the results
                self._calculator = calculator
                self._modulus_polynomial = modulus_string

                # Call the completion callback with the result
                on_complete(modulus_string)
            except ValueError as e:
                on_complete(f"Error: {str(e)}")
            except Exception as e:
                on_complete(f"Unexpected error: {str(e)}")

        # Start initialization in a separate thread
        init_thread = Thread(target=_initialize)
        init_thread.daemon = True  # Thread will exit when main program exits
        init_thread.start()

    def reset_calculator(self) -> None:
        """
        Reset the calculator state.

        Clears the calculator instance and modulus polynomial when a field is deselected.
        """
        self._calculator = None
        self._modulus_polynomial = None

    def perform_calculation(self, poly1: List[int], poly2: List[int], operation: str) -> str:
        """
        Perform a calculation operation between two polynomials.

        Args:
            poly1: Coefficients of the first polynomial.
            poly2: Coefficients of the second polynomial.
            operation: String identifier of the operation to perform ("add", "subtract", etc.).

        Returns:
            A string containing the formatted result or an error message.
        """
        if not self._calculator:
            return "Error: No field selected"

        try:
            # Map string operation to enum
            operation_map = {
                "add": FieldOperation.ADD,
                "subtract": FieldOperation.SUBTRACT,
                "multiply": FieldOperation.MULTIPLY,
                "divide": FieldOperation.DIVIDE
            }

            if operation not in operation_map:
                return f"Error: Unknown operation {operation}"

            field_op = operation_map[operation]

            # Perform the calculation
            result = self._calculator.handle_operation(poly1, poly2, field_op)

            # Format the result nicely
            return f"Result: {result}"

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"