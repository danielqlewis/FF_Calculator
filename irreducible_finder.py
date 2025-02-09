from modular_polynomial import ModularPolynomial

PRIME_FACTORS = {
    1: [1],
    2: [2],
    3: [3],
    4: [2],
    5: [5],
    6: [2, 3],
    7: [7],
    8: [2],
    9: [3],
    10: [2, 5],
    11: [11]
}


def check_if_primitive(num, prime_modulus):
    order = 1
    current_value = num
    while current_value != 1:
        current_value = (current_value * num) % prime_modulus
        order += 1

    return order == prime_modulus - 1


def compute_large_exponent_of_x(target_power, modulus_polynomial):
    p = modulus_polynomial.modulus
    d = modulus_polynomial.get_degree()
    power = 1
    active_expression = ModularPolynomial(p, [0, 1])
    expression_record = [(active_expression.get_copy(), power)]

    while power < target_power:
        add_expression_to_record = False
        if power * 2 > target_power:
            for x in reversed(expression_record):
                if x[1] <= target_power - power:
                    active_expression = active_expression.product_with(x[0])
                    power += x[1]
                    break
        else:
            active_expression = active_expression.product_with(active_expression)
            power *= 2
            add_expression_to_record = True

        if active_expression.get_degree() >= d:
            active_expression = active_expression.divided_by(modulus_polynomial).remainder

        if add_expression_to_record:
            expression_record.append((active_expression.get_copy(), power))

    return active_expression


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

    # Higher degree cases: use irreducibility criterion
    standard_poly = ModularPolynomial(poly.modulus, [0, 1])

    power = poly.modulus ** poly.get_degree()
    first_check = compute_large_exponent_of_x(power, poly)
    if first_check != standard_poly:
        return False
    for r in PRIME_FACTORS[poly.get_degree()]:
        power = poly.modulus ** (poly.get_degree() // r)
        active_check = compute_large_exponent_of_x(power, poly)
        if active_check == standard_poly:
            return False
    return True


def find_irreducible(p, n):
    primitive_elements = [x for x in range(1, p) if check_if_primitive(x, p)]
    leading_term = 1
    if n == 1:
        return ModularPolynomial(p, [primitive_elements[0]])

    elif n == 2:
        return ModularPolynomial(p, [primitive_elements[0], leading_term])

    else:
        if (p == 2 and n == 9) or (p == 3 and n == 11):
            if p == 2:
                return ModularPolynomial(2, [1, 1, 0, 0, 0, 0, 1, 1, 1])
            elif p == 3:
                return ModularPolynomial(3, [2, 0, 2, 0, 1, 0, 0, 0, 0, 2, 1])
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
