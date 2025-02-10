from modular_polynomial import ModularPolynomial

class FiniteFieldCalculator:
    def __init__(self, prime_modulus, polynomial_modulus):
        self.prime_modulus = prime_modulus
        self.polynomial_modulus = polynomial_modulus

    def find_multiplicative_inverse(self, polynomial):
        """Find multiplicative inverse of polynomial in the field"""
        # Use extended Euclidean algorithm to find inverse
        # gcd(a,b) = ax + by
        # In our case, we want gcd(polynomial, modulus) = 1
        # Then x is our inverse
        dividend = self.polynomial_modulus
        divisor = polynomial
        quotient_list = []
        remainder_list = []
        while 1:
            division_result = dividend.divided_by(divisor)
            quotient = division_result.quotient
            remainder = division_result.remainder
            quotient_list.append(quotient)
            remainder_list.append(remainder)
            if remainder.is_constant():
                break
            else:
                dividend = divisor
                divisor = remainder
        if not remainder_list[-1].is_one():
            raise ValueError("Polynomial has no multiplicative inverse")
        intermediate_expressions = [quotient_list[0].get_negative(),
                                    quotient_list[0].product_with(quotient_list[1]).add_one()]
        for x in range(2, len(remainder_list)):
            product = quotient_list[x].product_with(intermediate_expressions[x-1])
            new_expression = product.subtract_from(intermediate_expressions[x-2])
            intermediate_expressions.append(new_expression)
        return intermediate_expressions[-1].divided_by(self.polynomial_modulus).remainder

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
