from modular_polynomial import ModularPolynomial

class FiniteFieldCalculator:
    def __init__(self, prime_modulus, polynomial_modulus):
        self.prime_modulus = prime_modulus
        self.polynomial_modulus = polynomial_modulus


    def handle_operation(self, coefficient_set_0, coefficient_set_1, op):
        polynomial0 = ModularPolynomial(self.prime_modulus, coefficient_set_0)
        polynomial1 = ModularPolynomial(self.prime_modulus, coefficient_set_1)

        if op == "add":
            return polynomial0.add_to(polynomial1)
        elif op == "subtract":
            return polynomial1.subtract_from(polynomial0)
        elif op == "divide":
            return polynomial0.divided_by(polynomial1).quotient
        elif op == "multiply":
            initial_expression = polynomial0.product_with(polynomial1)
            return initial_expression.divided_by(self.polynomial_modulus).remainder
