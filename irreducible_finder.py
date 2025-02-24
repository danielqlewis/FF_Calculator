from modular_polynomial import ModularPolynomial
from itertools import product

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
    11: [11],
    12: [2, 3]
}


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


def check_if_divides(potential_factor, polynomial):
    return polynomial.divided_by(potential_factor).remainder.is_zero()


def generate_monic_polynomials(degree, prime_modulus):
    if degree == 0:
        return []
    coeff_options = range(prime_modulus)
    return [list(coeffs) + [1] for coeffs in product(coeff_options, repeat=degree)]


def check_non_prime_power_degree(poly):
    for degree_divisor in [1, 2]:
        coefficients = generate_monic_polynomials(degree_divisor, poly.modulus)
        for potential_divisor_poly in coefficients:
            if check_if_divides(ModularPolynomial(poly.modulus, potential_divisor_poly), poly):
                return False

    return True


def check_if_low_degree_irreducible(poly, deg):
    if deg == 0:
        return poly.coefficients[0] != 0

    if deg == 1:
        return True

    # Degree 2 or 3 case: check for roots
    if deg in [2, 3]:
        for x in range(poly.modulus):
            if poly.evaluate(x) == 0:
                return False
        return True


def check_if_high_degree_irreducible(poly, deg):
    standard_poly = ModularPolynomial(poly.modulus, [0, 1])
    power = poly.modulus ** deg

    first_check = compute_large_exponent_of_x(power, poly)
    if first_check != standard_poly:
        return False

    for r in PRIME_FACTORS[deg]:
        power = poly.modulus ** (deg // r)
        active_check = compute_large_exponent_of_x(power, poly)
        if active_check == standard_poly:
            return False

    return True


def check_if_irreducible(poly):
    deg = poly.get_degree()
    if deg <= 3:
        if not check_if_low_degree_irreducible(poly, deg):
            return False
    else:
        if not check_if_high_degree_irreducible(poly, deg):
            return False

    if deg in [6, 10, 12]:
        if not check_non_prime_power_degree(poly):
            return False

    return True


def check_if_primitive(num, prime_modulus):
    order = 1
    current_value = num
    while current_value != 1:
        current_value = (current_value * num) % prime_modulus
        order += 1

    return order == prime_modulus - 1


def find_irreducible_trinomial(p, d):
    primitive_elements = [x for x in range(1, p) if check_if_primitive(x, p)]
    leading_term = 1

    for constant in primitive_elements + [1]:
        for y in range(1, p):
            for x in range(1, d):
                lower_term_zeros = [0] * (x - 1)
                higher_term_zeros = [0] * (d - x - 1)
                coefficient_set = [constant] + lower_term_zeros + [y] + higher_term_zeros + [leading_term]
                polynomial = ModularPolynomial(p, coefficient_set)
                if check_if_irreducible(polynomial):
                    return polynomial



def find_irreducible(p, d):
    if d == 1:
        return ModularPolynomial(p, [0, 1])

    # This special case occur because F₂ does not have an irreducible trinomial
    # of degree 8 requiring a polynomials with more terms.
    elif p == 2 and d == 8:
        return ModularPolynomial(2, [1, 1, 0, 0, 0, 0, 1, 1, 1])

    else:
        return find_irreducible_trinomial(p, d)

