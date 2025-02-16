from typing import List

class DivisionResult:
    """Container for results of polynomial division."""
    def __init__(self, q: 'ModularPolynomial', r: 'ModularPolynomial'):
        self.quotient = q
        self.remainder = r


class ModularPolynomial:
    """
    A class representing polynomials with coefficients in Z/nZ (integers modulo n).
    Supports standard polynomial operations with coefficients reduced modulo n.
    """
    def __init__(self, modulus: int, raw_coefficients: List[int]):
        """
        Initialize a polynomial with coefficients in Z/nZ.

        Args:
            modulus: The modulus n for the coefficient ring Z/nZ. Must be positive.
            raw_coefficients: List of coefficients from lowest to highest degree.
                            Will be normalized modulo n with trailing zeros removed.

        Raises:
            ValueError: If modulus is not positive.
        """
        if modulus <= 0:
            raise ValueError("Modulus must be positive")
        self.modulus = modulus
        # Remove trailing zeros and normalize coefficients
        while raw_coefficients and raw_coefficients[-1] % modulus == 0:
            raw_coefficients.pop()
        self.coefficients = [x % modulus for x in raw_coefficients] if raw_coefficients else [0]

    def __str__(self) -> str:
        """
        Convert polynomial to string in standard mathematical notation.

        Returns:
            String representation of polynomial in form: ax^n + bx^(n-1) + ... + k mod p
        """
        if not self.coefficients or all(c == 0 for c in self.coefficients):
            return "0 mod " + str(self.modulus)

        terms = []
        for i, coeff in enumerate(reversed(self.coefficients)):
            if coeff == 0:
                continue

            power = len(self.coefficients) - 1 - i

            # Handle coefficient part
            if power == 0:
                terms.append(str(coeff))
            elif coeff == 1:
                if power == 1:
                    terms.append('x')
                else:
                    terms.append(f'x^{power}')
            else:
                if power == 1:
                    terms.append(f'{coeff}x')
                else:
                    terms.append(f'{coeff}x^{power}')

        return " + ".join(terms) + " mod " + str(self.modulus)

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another ModularPolynomial.

        Returns:
            True if other is a ModularPolynomial with same modulus and coefficients.
        """
        if not isinstance(other, ModularPolynomial):
            return False
        return self.modulus == other.modulus and self.coefficients == other.coefficients

    def get_degree(self) -> int:
        """
        Get the degree of the polynomial.

        Returns:
            The highest power of x with non-zero coefficient.
        """
        return len(self.coefficients) - 1

    def get_lead_coefficient(self) -> int:
        """
        Get the leading coefficient of the polynomial.

        Returns:
            The coefficient of the highest degree term.
        """
        return self.coefficients[-1]

    def get_copy(self) -> 'ModularPolynomial':
        """
        Create a deep copy of this polynomial.

        Returns:
            A new ModularPolynomial with the same modulus and coefficients.
        """
        return ModularPolynomial(self.modulus, self.coefficients.copy())

    def get_negative(self) -> 'ModularPolynomial':
        """
        Create a deep copy of the additive inverse of this polynomial.

        Returns:
            A new ModularPolynomial with the same modulus and inverse coefficients.
        """
        return ModularPolynomial(self.modulus, [self.modulus - x for x in self.coefficients])
    
    def is_zero(self) -> bool:
        """
        Check if this is the zero polynomial.

        Returns:
            True if this instance is the zero polynomial, False otherwise.
        """
        return len(self.coefficients) == 1 and self.coefficients[0] == 0

    def is_one(self) -> bool:
        """
        Check if this is the unit polynomial.

        Returns:
            True if this instance is the unit polynomial, False otherwise.
        """
        return len(self.coefficients) == 1 and self.coefficients[0] == 1

    def is_constant(self):
        """
        Check if this is a constant polynomial.

        Returns:
            True if this instance is a constant polynomial, False otherwise.
        """
        return len(self.coefficients) == 1
    
    def evaluate(self, arg: int) -> int:
        """
        Evaluate the polynomial at a given value using Horner's method.

        Args:
            arg: Value to evaluate the polynomial at.

        Returns:
            Value of polynomial at arg, reduced modulo the polynomial's modulus.
        """
        # Use Horner's method for more efficient evaluation
        result = 0
        for coeff in reversed(self.coefficients):
            result = (result * arg + coeff) % self.modulus
        return result

    def add_to(self, other: 'ModularPolynomial', negative: bool = False) -> 'ModularPolynomial':
        """
        Add (or subtract) another polynomial to this one.

        Args:
            other: Another ModularPolynomial instance to add to this one.
            negative: If True, subtract instead of add.

        Returns:
            A new ModularPolynomial representing the sum (or difference).

        Raises:
            ValueError: If polynomials have different moduli.
        """
        if self.modulus != other.modulus:
            raise ValueError("Polynomials must have the same modulus [Addition]")

        # Get the maximum length needed
        max_len = max(len(self.coefficients), len(other.coefficients))

        # Create new coefficients list with padded zeros as needed
        new_coefficients = []
        for i in range(max_len):
            # Get coefficients or 0 if index is out of range
            a = self.coefficients[i] if i < len(self.coefficients) else 0
            if negative:
                b = self.modulus - other.coefficients[i] if i < len(other.coefficients) else 0
            else:
                b = other.coefficients[i] if i < len(other.coefficients) else 0
            new_coefficients.append((a + b) % self.modulus)

        return ModularPolynomial(self.modulus, new_coefficients)

    def add_one(self):
        """
        return a new polynomial equal to the sum of this polynomial and one
        """
        polynomial_one = ModularPolynomial(self.modulus, [1])
        return self.add_to(polynomial_one)
    
    def subtract_from(self, other: 'ModularPolynomial') -> 'ModularPolynomial':
        """
        Subtract this polynomial from another one.

        Args:
            other: The polynomial to subtract from.

        Returns:
            A new ModularPolynomial representing (other - self).
        """
        return other.add_to(self, True)

    def product_with(self, other: 'ModularPolynomial') -> 'ModularPolynomial':
        """
        Multiply this polynomial by another one.

        Args:
            other: The polynomial to multiply by.

        Returns:
            A new ModularPolynomial representing the product.

        Raises:
            ValueError: If polynomials have different moduli.
        """
        if self.modulus != other.modulus:
            raise ValueError("Polynomials must have the same modulus [Multiplication]")

        # Initialize result coefficients with zeros
        degree = len(self.coefficients) + len(other.coefficients) - 1
        result = [0] * degree

        # Multiply term by term
        for i, a in enumerate(self.coefficients):
            for j, b in enumerate(other.coefficients):
                result[i + j] = (result[i + j] + a * b) % self.modulus

        return ModularPolynomial(self.modulus, result)

    def divided_by(self, other: 'ModularPolynomial') -> 'DivisionResult':
        """
        Divide this polynomial by another using polynomial long division.

        Args:
            other: The polynomial to divide by.

        Returns:
            DivisionResult containing quotient and remainder polynomials such that
            self = (other × quotient) + remainder
            where degree(remainder) < degree(other) or remainder = 0

        Raises:
            ValueError: If polynomials have different moduli or if other is zero.

        Note:
            Assumes the modulus is prime to compute multiplicative inverses.
        """
        if self.modulus != other.modulus:
            raise ValueError("Polynomials must have the same modulus [Division]")
        if not other.coefficients or all(c == 0 for c in other.coefficients):
            raise ValueError("Cannot divide by zero polynomial")

        quotient = ModularPolynomial(self.modulus, [0])
        remainder = self.get_copy()

        while remainder.get_degree() >= other.get_degree() and not remainder.is_zero():
            #to build the quotient term we need to find its degree and its coefficient
            qt_degree = remainder.get_degree() - other.get_degree()
            #By assuming the modulus is prime, we can use Eulers Theorem (a^-1 = a^(m -2)):
            other_lead_inverse = (other.get_lead_coefficient() ** (self.modulus - 2)) % self.modulus
            qt_coefficient = remainder.get_lead_coefficient() * other_lead_inverse
            quotient_term = ModularPolynomial(self.modulus, [0] * qt_degree + [qt_coefficient])
            intermediate_expression = other.product_with(quotient_term)
            quotient = quotient.add_to(quotient_term)
            remainder = intermediate_expression.subtract_from(remainder)

        return DivisionResult(quotient, remainder)
