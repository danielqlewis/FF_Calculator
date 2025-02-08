from modular_polynomial import ModularPolynomial


def check_if_primitive(num, prime_modulus):
    order = 1
    current_value = num
    while current_value != 1:
        current_value = (current_value * num) % prime_modulus
        order += 1

    return order == prime_modulus - 1


def check_if_irreducible(poly):
    # Degree 0 case
    if poly.get_degree() == 0:
        return poly.coefficients[0] != 0

    # Degree 1 case
    if poly.get_degree() == 1:
        return True

    # Degree 2 or 3 case: check for roots
    if poly.get_degree() <= 3:
        for x in range(poly.modulus):
            if poly.evaluate(x) == 0:
                return False
        return True

    # Higher degrees will need a different approach
    raise NotImplementedError("Irreducibility test not implemented for degree >= 4")


def find_irreducible(p, n):
    primitive_elements = [x for x in range(1, p) if check_if_primitive(x, p)]
    leading_term = 1
    if n == 1:
        return ModularPolynomial(p, [primitive_elements[0]])

    elif n == 2:
        return ModularPolynomial(p, [primitive_elements[0], leading_term])

    else:
        for constant in primitive_elements:
            for y in range(1, p):
                for x in range(1, n - 1):
                    lower_term_zeros = [0] * (x - 1)
                    higher_term_zeros = [0] * (n - x - 2)
                    coefficient_set = [constant] + lower_term_zeros + [y] + higher_term_zeros + [leading_term]
                    polynomial = ModularPolynomial(p, coefficient_set)
                    if check_if_irreducible(polynomial):
                        return polynomial
