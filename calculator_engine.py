from modular_polynomial import ModularPolynomial
from irreducible_finder import find_irreducible
from enum import Enum
from typing import List, Tuple

PRIME_LIST = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]


class FieldOperation(Enum):
    """
    Enumeration of supported finite field arithmetic operations.
    """
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


class FiniteFieldCalculator:
    """
    Calculator for performing arithmetic in finite field extensions.

    This class provides functionality to perform operations in the finite field GF(p^n),
    represented as polynomials modulo an irreducible polynomial of degree n over GF(p).
    """
    def __init__(self, prime_modulus: int, dim: int):
        """
        Initialize a calculator for the finite field GF(p^n).

        Args:
            prime_modulus: The prime characteristic p of the base field.
            dim: The dimension n of the field extension (degree of the extension).

        Raises:
            ValueError: If the provided modulus is not in the supported prime list.
        """
        if prime_modulus not in PRIME_LIST:
            raise ValueError("Invalid modulus")
        self.prime_modulus = prime_modulus
        self.polynomial_modulus = find_irreducible(prime_modulus, dim)

    def _reduce_by_modulus(self, poly: 'ModularPolynomial') -> 'ModularPolynomial':
        """
        Reduce a polynomial modulo the field's irreducible polynomial.

        Args:
            poly: The polynomial to reduce.

        Returns:
            A new ModularPolynomial equal to The remainder when dividing by
            the field's irreducible polynomial.
        """
        return poly.divided_by(self.polynomial_modulus).remainder

    def _find_constant_inverse(self, polynomial: 'ModularPolynomial') -> 'ModularPolynomial':
        """
        Find the multiplicative inverse of a constant polynomial.

        Uses Euler's Theorem: a^(p-2) = a^(-1) mod p for prime p.

        Args:
            polynomial: A constant polynomial whose constant term needs inversion.

        Returns:
            A constant polynomial representing the inverse.
        """
        constant_inverse = polynomial.coefficients[0] ** (self.prime_modulus - 2)
        return ModularPolynomial(self.prime_modulus, [constant_inverse])

    def _compute_euclidean_sequence(self, polynomial: 'ModularPolynomial') -> Tuple[
        List['ModularPolynomial'], List['ModularPolynomial']]:
        """
        Compute the sequence of quotients and remainders in the Extended Euclidean Algorithm.

        This is used in finding the multiplicative inverse of a non-constant polynomial.

        Args:
            polynomial: The polynomial to find the inverse for.

        Returns:
            A tuple containing two lists:
            - quotients: The sequence of quotient polynomials
            - remainders: The sequence of remainder polynomials
        """
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
    def _compute_expression_from_sequence(quotient_list: List['ModularPolynomial'],
                                          remainder_count: int) -> 'ModularPolynomial':
        """
        Compute the Bézout coefficient for the original polynomial from the Euclidean sequence.

        Uses the quotient sequence to work backwards and find the polynomial expression
        needed in the Extended Euclidean Algorithm.

        Args:
            quotient_list: The list of quotients from the Euclidean Algorithm.
            remainder_count: The number of remainders (including the final constant).

        Returns:
            A polynomial expression that, when properly combined with the final remainder,
            gives the multiplicative inverse.
        """
        intermediate_expressions = [quotient_list[0].get_negative()]

        if len(quotient_list) > 1:
            intermediate_expressions.append(quotient_list[0].product_with(quotient_list[1]).add_one())

        for x in range(2, remainder_count):
            product = quotient_list[x].product_with(intermediate_expressions[x - 1])
            new_expression = product.subtract_from(intermediate_expressions[x - 2])
            intermediate_expressions.append(new_expression)

        return intermediate_expressions[-1]

    def find_multiplicative_inverse(self, polynomial: 'ModularPolynomial') -> 'ModularPolynomial':
        """
        Find the multiplicative inverse of a polynomial in the finite field.

        Implements the Extended Euclidean Algorithm for polynomials to find an element
        x such that polynomial * x ≡ 1 (mod polynomial_modulus).

        Args:
            polynomial: The polynomial to find the inverse for.

        Returns:
            The multiplicative inverse of the polynomial in the finite field.

        Raises:
            ValueError: If the input is the zero polynomial, which has no inverse.
        """
        if polynomial.is_zero():
            raise ValueError("Zero polynomial does not have an inverse")

        if polynomial.is_constant():
            return self._find_constant_inverse(polynomial)

        quotients, remainders = self._compute_euclidean_sequence(polynomial)
        final_constant_inverse = self._find_constant_inverse(remainders[-1])
        initial_expression = self._compute_expression_from_sequence(quotients, len(remainders))

        reduced_expression = self._reduce_by_modulus(initial_expression)
        return reduced_expression.product_with(final_constant_inverse)

    def handle_operation(self, coefficient_set_0: List[int], coefficient_set_1: List[int],
                         op: FieldOperation) -> 'ModularPolynomial':
        """
        Perform the specified arithmetic operation between two field elements.

        Args:
            coefficient_set_0: Coefficients of the first polynomial operand.
            coefficient_set_1: Coefficients of the second polynomial operand.
            op: The operation to perform (ADD, SUBTRACT, MULTIPLY, or DIVIDE).

        Returns:
            The result of the operation as a ModularPolynomial.

        Raises:
            ValueError: If dividing by zero or if an unknown operation is specified.
        """
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
