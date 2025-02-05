class DivisionResult:
    def __init__(self, q, r):
        self.quotient = q
        self.remainder = r


class ModularPolynomial:
    def __init__(self, modulus, raw_coefficients):
        if modulus <= 0:
            raise ValueError("Modulus must be positive")
        self.modulus = modulus
        # Remove trailing zeros and normalize coefficients
        while raw_coefficients and raw_coefficients[-1] == 0:
            raw_coefficients.pop()
        self.coefficients = [x % modulus for x in raw_coefficients] if raw_coefficients else [0]

    def __str__(self):
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

    def get_degree(self):
        return len(self.coefficients) - 1

    def get_lead_coefficient(self):
        return self.coefficients[-1]

    def get_copy(self):
        return ModularPolynomial(self.modulus, self.coefficients)

    def evaluate(self, arg):
        # Use Horner's method for more efficient evaluation
        result = 0
        for coeff in reversed(self.coefficients):
            result = (result * arg + coeff) % self.modulus
        return result

    def __eq__(self, other):
        if not isinstance(other, ModularPolynomial):
            return False
        return self.modulus == other.modulus and self.coefficients == other.coefficients

    def add_to(self, other, negative=False):
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

    def subtract_from(self, other):
        return other.add_to(self, True)

    def product_with(self, other):
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

    def divided_by(self, other):
        if self.modulus != other.modulus:
            raise ValueError("Polynomials must have the same modulus [Division]")
        if not other.coefficients or all(c == 0 for c in other.coefficients):
            raise ValueError("Cannot divide by zero polynomial")

        quotient = ModularPolynomial(self.modulus, [0])
        remainder = self.get_copy()

        while remainder.get_degree() >= other.get_degree() and remainder.get_degree() > 0:
            qt_degree = remainder.get_degree() - other.get_degree()
            #By assuming the modulus is prime, we can use Eulers Theorem:
            other_lead_inverse = (other.get_lead_coefficient() ** (self.modulus - 2)) % self.modulus
            qt_coefficient = remainder.get_lead_coefficient() * other_lead_inverse
            quotient_term = ModularPolynomial(self.modulus, [0] * qt_degree + [qt_coefficient])
            intermediate_expression = other.product_with(quotient_term)
            quotient = quotient.add_to(quotient_term)
            remainder = intermediate_expression.subtract_from(remainder)

        return DivisionResult(quotient, remainder)