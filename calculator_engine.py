from modular_polynomial import ModularPolynomial
from irreducible_finder import find_irreducible

prime_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]

class FiniteFieldCalculator:
    def __init__(self, prime_modulus, dim):
        if prime_modulus not in prime_list:
            raise ValueError("Invalid modulus")
        self.prime_modulus = prime_modulus
        self.polynomial_modulus = find_irreducible(prime_modulus, dim)

    def find_multiplicative_inverse(self, polynomial):
        """Find multiplicative inverse of polynomial in the field"""
        if polynomial.is_zero():
            raise ValueError("Zero polynomial does not have an inverse")
        if polynomial.is_constant():
            constant_inverse = polynomial.coefficients[0] ** (self.prime_modulus - 2)
            return ModularPolynomial(self.prime_modulus, [constant_inverse])
        # Use extended Euclidean algorithm to find inverse
        # gcd(a,b) = ax + by
        # In our case, we want gcd(polynomial, modulus) = 1
        # Then x is our inverse
        dividend = self.polynomial_modulus
        divisor = polynomial
        quotient_list = []
        remainder_list = []
        final_constant_inverse = 1
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
            final_constant_inverse = remainder_list[-1].coefficients[0] ** (self.prime_modulus - 2)
            
        intermediate_expressions = [quotient_list[0].get_negative()]

        
        if len(quotient_list) > 1:
            intermediate_expressions.append(quotient_list[0].product_with(quotient_list[1]).add_one())

        
        for x in range(2, len(remainder_list)):
            product = quotient_list[x].product_with(intermediate_expressions[x-1])
            new_expression = product.subtract_from(intermediate_expressions[x-2])
            intermediate_expressions.append(new_expression)

        raw_result = intermediate_expressions[-1].divided_by(self.polynomial_modulus).remainder
        return raw_result.product_with(ModularPolynomial(self.prime_modulus, [final_constant_inverse]))

    def handle_operation(self, coefficient_set_0, coefficient_set_1, op):
        polynomial0 = ModularPolynomial(self.prime_modulus, coefficient_set_0)
        polynomial1 = ModularPolynomial(self.prime_modulus, coefficient_set_1)

        if op == "add":
            return polynomial0.add_to(polynomial1)
        elif op == "subtract":
            return polynomial1.subtract_from(polynomial0)
        elif op == "divide":
            if polynomial1.is_zero():
                raise ValueError("Cannot divide by zero polynomial")
            polynomial1_inverse = self.find_multiplicative_inverse(polynomial1)
            product = polynomial0.product_with(polynomial1_inverse)
            return product.divided_by(self.polynomial_modulus).remainder
        elif op == "multiply":
            product = polynomial0.product_with(polynomial1)
            return product.divided_by(self.polynomial_modulus).remainder
