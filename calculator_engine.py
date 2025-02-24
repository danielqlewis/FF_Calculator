from modular_polynomial import ModularPolynomial
from irreducible_finder import find_irreducible
from enum import Enum

PRIME_LIST = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]


class FieldOperation(Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


class FiniteFieldCalculator:
    def __init__(self, prime_modulus, dim):
        if prime_modulus not in PRIME_LIST:
            raise ValueError("Invalid modulus")
        self.prime_modulus = prime_modulus
        self.polynomial_modulus = find_irreducible(prime_modulus, dim)

    def _reduce_by_modulus(self, poly):
        return poly.divided_by(self.polynomial_modulus).remainder

    def _find_constant_inverse(self, polynomial):
        constant_inverse = polynomial.coefficients[0] ** (self.prime_modulus - 2)
        return ModularPolynomial(self.prime_modulus, [constant_inverse])

    def _compute_euclidean_sequence(self, polynomial):
        dividend = self.polynomial_modulus
        divisor = polynomial
        quotients = []
        remainders = []

        while True:
            division_result = dividend.divided_by(divisor)
            quotients.append(division_result.quotient)
            remainders.append(division_result.remainder)

            if division_result.remainder.is_constant():
                break

            dividend = divisor
            divisor = division_result.remainder

        return quotients, remainders

    @staticmethod
    def _compute_expression_from_sequence(quotient_list, remainder_count):
        intermediate_expressions = [quotient_list[0].get_negative()]

        if len(quotient_list) > 1:
            intermediate_expressions.append(quotient_list[0].product_with(quotient_list[1]).add_one())

        for x in range(2, remainder_count):
            product = quotient_list[x].product_with(intermediate_expressions[x - 1])
            new_expression = product.subtract_from(intermediate_expressions[x - 2])
            intermediate_expressions.append(new_expression)

        return intermediate_expressions[-1]

    def find_multiplicative_inverse(self, polynomial):
        if polynomial.is_zero():
            raise ValueError("Zero polynomial does not have an inverse")

        if polynomial.is_constant():
            return self._find_constant_inverse(polynomial)

        quotients, remainders = self._compute_euclidean_sequence(polynomial)
        final_constant_inverse = self._find_constant_inverse(remainders[-1])
        initial_expression = self._compute_expression_from_sequence(quotients, len(remainders))

        reduced_expression = self._reduce_by_modulus(initial_expression)
        return reduced_expression.product_with(final_constant_inverse)

    def handle_operation(self, coefficient_set_0, coefficient_set_1, op):
        polynomial0 = ModularPolynomial(self.prime_modulus, coefficient_set_0)
        polynomial1 = ModularPolynomial(self.prime_modulus, coefficient_set_1)

        if op == FieldOperation.ADD:
            return polynomial0.add_to(polynomial1)
        elif op == FieldOperation.SUBTRACT:
            return polynomial1.subtract_from(polynomial0)
        elif op == FieldOperation.MULTIPLY:
            product = polynomial0.product_with(polynomial1)
            return self._reduce_by_modulus(product)
        elif op == FieldOperation.DIVIDE:
            if polynomial1.is_zero():
                raise ValueError("Cannot divide by zero polynomial")
            polynomial1_inverse = self.find_multiplicative_inverse(polynomial1)
            product = polynomial0.product_with(polynomial1_inverse)
            return self._reduce_by_modulus(product)
        else:
            raise ValueError(f"Unknown operation: {op}")