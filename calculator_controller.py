import threading
from typing import List, Callable

from calculator_engine import FiniteFieldCalculator, FieldOperation


class CalculatorController:
    def __init__(self):
        self.calculator = None
        self.modulus_polynomial = None

    def initialize_field_async(self, p: int, n: int, on_complete: Callable[[str], None]) -> None:
        def _initialize():
            try:
                calculator = FiniteFieldCalculator(p, n)
                modulus_string = str(calculator.polynomial_modulus)

                # Store the results
                self.calculator = calculator
                self.modulus_polynomial = modulus_string

                # Call the completion callback with the result
                on_complete(modulus_string)
            except ValueError as e:
                on_complete(f"Error: {str(e)}")
            except Exception as e:
                on_complete(f"Unexpected error: {str(e)}")

        # Start initialization in a separate thread
        thread = threading.Thread(target=_initialize)
        thread.daemon = True  # Thread will exit when main program exits
        thread.start()

    def reset_calculator(self) -> None:
        self.calculator = None
        self.modulus_polynomial = None

    def perform_calculation(self, poly1: List[int], poly2: List[int], operation: str) -> str:
        if not self.calculator:
            return "Error: No field selected"

        try:
            # Map string operation to enum
            op_map = {
                "add": FieldOperation.ADD,
                "subtract": FieldOperation.SUBTRACT,
                "multiply": FieldOperation.MULTIPLY,
                "divide": FieldOperation.DIVIDE
            }

            if operation not in op_map:
                return f"Error: Unknown operation {operation}"

            field_op = op_map[operation]

            # Perform the calculation
            result = self.calculator.handle_operation(poly1, poly2, field_op)

            # Format the result nicely
            return f"Result: {result}"

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"