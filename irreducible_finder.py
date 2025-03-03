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


def compute_large_exponent_of_x(target_power: int, modulus_polynomial: 'ModularPolynomial') -> 'ModularPolynomial':
    """
    Compute x^(target_power) mod modulus_polynomial efficiently using repeated squaring.

    Args:
        target_power: The exponent to raise x to.
        modulus_polynomial: The polynomial to reduce by.

    Returns:
        A ModularPolynomial representing x^(target_power) mod modulus_polynomial.
    """
    p = modulus_polynomial.modulus
    d = modulus_polynomial.get_degree()

    # Initialize with x^1 (the polynomial x)
    power = 1
    active_expression = ModularPolynomial(p, [0, 1])

    # Keep track of computed powers for reuse
    expression_record = [(active_expression.get_copy(), power)]

    while power < target_power:
        add_expression_to_record = False

        # Strategy: If doubling exceeds target, look for largest previously
        # computed power that can be used
        if power * 2 > target_power:
            for x in reversed(expression_record):
                # Find the largest power that doesn't exceed what we need and multiply by it
                if x[1] <= target_power - power:
                    active_expression = active_expression.product_with(x[0])
                    power += x[1]
                    break
        else:
            # Square the current expression
            active_expression = active_expression.product_with(active_expression)
            power *= 2
            add_expression_to_record = True

        # If degree is too large, reduce by the modulus polynomial
        if active_expression.get_degree() >= d:
            active_expression = active_expression.divided_by(modulus_polynomial).remainder

        # If squared, store newly computed power for potential future use
        if add_expression_to_record:
            expression_record.append((active_expression.get_copy(), power))

    return active_expression


def check_non_prime_power_degree(poly: 'ModularPolynomial') -> bool:
    """
    Check if a polynomial with non-prime-power degree is irreducible by testing
    for divisibility by potential low-degree factors.

    Args:
        poly: The ModularPolynomial to check.

    Returns:
        False if a low-degree factor was found, True otherwise.
    """
    coeff_options = range(poly.modulus)
    for degree in [1, 2]:
        # Generate all possible polynomials of the current degree with monic leading term
        # product() generates all combinations of coefficients for the lower terms
        coefficients = [list(coeffs) + [1] for coeffs in product(coeff_options, repeat=degree)]
        for potential_divisor_coefficients in coefficients:
            potential_divisor = ModularPolynomial(poly.modulus, potential_divisor_coefficients)
            # If remainder is zero, we've found a factor, so poly is reducible
            if poly.divided_by(potential_divisor).remainder.is_zero():
                return False

    return True


def check_if_low_degree_irreducible(poly: 'ModularPolynomial', deg: int) -> bool:
    """
    Check if a low-degree polynomial (degree ≤ 3) is irreducible.

    Args:
        poly: The ModularPolynomial to check.
        deg: The degree of the polynomial.

    Returns:
        True if the polynomial is irreducible, False otherwise.
    """
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


def check_if_high_degree_irreducible(poly: 'ModularPolynomial', deg: int) -> bool:
    """
    Check if a higher-degree polynomial (degree > 3) is irreducible using
    a modified version of Rabin's irreducibility test.

    Args:
        poly: The ModularPolynomial to check.
        deg: The degree of the polynomial.

    Returns:
        True if the test indicates the polynomial is irreducible, False otherwise.

    Note:
        This implementation uses an optimized version of Rabin's test that works
        perfectly for prime power degrees, but may require additional verification
        for non-prime power degrees. See the design documentation for complete details.
    """
    standard_poly = ModularPolynomial(poly.modulus, [0, 1])
    power = poly.modulus ** deg

    # check that x^power not equal x mod input poly
    first_check = compute_large_exponent_of_x(power, poly)
    if first_check != standard_poly:
        return False

    # check that x^(power/r) is equal x mod input poly for each prime r dividing power
    for r in PRIME_FACTORS[deg]:
        power = poly.modulus ** (deg // r)
        active_check = compute_large_exponent_of_x(power, poly)
        if active_check == standard_poly:
            return False

    return True


def check_if_irreducible(poly: 'ModularPolynomial') -> bool:
    """
    Check if a polynomial is irreducible over its coefficient field.

    This function applies different strategies based on polynomial degree:
    - For degrees ≤ 3: Direct testing for roots or factors
    - For higher degrees: Modified Rabin's irreducibility test
    - For specific non-prime power degrees (6, 10, 12): Additional checks for low-degree factors

    Args:
        poly: The ModularPolynomial to check for irreducibility.

    Returns:
        True if the polynomial is irreducible, False otherwise.
    """
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


def check_if_primitive(num: int, prime_modulus: int) -> bool:
    """
    Check if a number is primitive (generator) in the field Z/pZ.

    A number is primitive if it generates all non-zero elements of the field
    under multiplication.

    Args:
        num: The number to check.
        prime_modulus: The prime modulus of the field.

    Returns:
        True if the number is primitive, False otherwise.
    """
    order = 1
    current_value = num
    while current_value != 1:
        current_value = (current_value * num) % prime_modulus
        order += 1

    return order == prime_modulus - 1


def find_irreducible_trinomial(characteristic: int, degree: int) -> 'ModularPolynomial':
    """
    Find an irreducible trinomial (polynomial with exactly three terms) of the
    specified degree over the finite field of given characteristic.

    Args:
        characteristic: The characteristic of the field (must be prime).
        degree: The degree of the trinomial to find.

    Returns:
        A ModularPolynomial representing an irreducible trinomial.
    """
    primitive_elements = [x for x in range(1, characteristic) if check_if_primitive(x, characteristic)]
    leading_term = 1

    for constant in primitive_elements + [1]:
        # Try all possible non-zero coefficients for the middle term
        for y in range(1, characteristic):
            # Try all possible positions for the middle term
            for z in range(1, degree):
                # Construct the trinomial: constant + y*x^z + x^degree
                # Form: [constant, 0, 0, ..., y, 0, 0, ..., 1]
                lower_term_zeros = [0] * (z - 1)             # Zeros between constant and middle term
                higher_term_zeros = [0] * (degree - z - 1)   # Zeros between middle term and leading term
                coefficient_set = [constant] + lower_term_zeros + [y] + higher_term_zeros + [leading_term]

                polynomial = ModularPolynomial(characteristic, coefficient_set)
                if check_if_irreducible(polynomial):
                    return polynomial



def find_irreducible(characteristic: int, degree: int) -> 'ModularPolynomial':
    """
    Find an irreducible polynomial of the specified degree over the finite field
    of given characteristic.

    Args:
        characteristic: The characteristic of the field (must be prime).
        degree: The degree of the irreducible polynomial to find.

    Returns:
        A ModularPolynomial that is irreducible over the specified field.

    Note:
        For most cases, returns an irreducible trinomial.
        The special case of characteristic 2, degree 8 is handled spearately
    """
    if degree == 1:
        return ModularPolynomial(characteristic, [0, 1])

    # This special case occur because F₂ does not have an irreducible trinomial
    # of degree 8 requiring a polynomials with more terms.
    elif characteristic == 2 and degree == 8:
        return ModularPolynomial(2, [1, 1, 0, 0, 0, 0, 1, 1, 1])

    else:
        return find_irreducible_trinomial(characteristic, degree)

