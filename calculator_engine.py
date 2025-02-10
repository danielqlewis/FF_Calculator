from modular_polynomial import ModularPolynomial

class FiniteFieldCalculator:
    def __init__(self, prime_modulus, polynomial_modulus):
        self.prime_modulus = prime_modulus
        self.polynomial_modulus = polynomial_modulus

    def find_multiplicative_inverse(self, polynomial):
        """Find multiplicative inverse of polynomial in the field"""
        raise NotImplementedError()

    def handle_operation(self, coefficient_set_0, coefficient_set_1, op):
        polynomial0 = ModularPolynomial(self.prime_modulus, coefficient_set_0)
        polynomial1 = ModularPolynomial(self.prime_modulus, coefficient_set_1)

        if op == "add":
            return polynomial0.add_to(polynomial1)
        elif op == "subtract":
            return polynomial1.subtract_from(polynomial0)
        elif op == "divide":
            polynomial1_inverse = self.find_multiplicative_inverse(polynomial1)
            product = polynomial0.product_with(polynomial1_inverse)
            return product.divided_by(self.polynomial_modulus).remainder
        elif op == "multiply":
            product = polynomial0.product_with(polynomial1)
            return product.divided_by(self.polynomial_modulus).remainder
