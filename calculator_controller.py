from typing import List

from calculator_engine import FiniteFieldCalculator, FieldOperation


class CalculatorController:
    def __init__(self):
        self.calculator = None
        self.modulus_polynomial = None

    def initialize_field(self, p: int, n: int) -> str:
        try:
            self.calculator = FiniteFieldCalculator(p, n)
            self.modulus_polynomial = str(self.calculator.polynomial_modulus)
            return self.modulus_polynomial
        except ValueError as e:
            return f"Error: {str(e)}"

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