import unittest

import calculator_engine
from modular_polynomial import ModularPolynomial, DivisionResult
from irreducible_finder import (
    check_if_primitive,
    compute_large_exponent_of_x,
    check_if_irreducible,
    find_irreducible,
    PRIME_FACTORS
)
from calculator_engine import FiniteFieldCalculator
import random


class TestModularPolynomial(unittest.TestCase):
    def test_init_basic(self):
        """Test basic polynomial initialization"""
        # Test zero polynomial
        p = ModularPolynomial(5, [])
        self.assertEqual(p.coefficients, [0])
        self.assertEqual(p.modulus, 5)

        # Test simple polynomial
        p = ModularPolynomial(7, [1, 2, 3])  # 3x^2 + 2x + 1 mod 7
        self.assertEqual(p.coefficients, [1, 2, 3])
        self.assertEqual(p.modulus, 7)

    def test_init_coefficient_normalization(self):
        """Test that coefficients are properly normalized modulo n"""
        # Test coefficient reduction
        p = ModularPolynomial(5, [6, 7, 8])  # Should become 3x^2 + 2x + 1 mod 5
        self.assertEqual(p.coefficients, [1, 2, 3])

        # Test trailing zeros removal
        p = ModularPolynomial(3, [1, 2, 0, 0])  # Should become 2x + 1 mod 3
        self.assertEqual(p.coefficients, [1, 2])

    def test_additional_init_normalizations(self):
        """Test additional coefficient normalization cases"""
        # Test normalization of negative coefficients
        p = ModularPolynomial(5, [-1, -2, -3])  # Should become 4x^2 + 3x + 2 mod 5
        self.assertEqual(p.coefficients, [4, 3, 2])

        # Test alternating positive/negative coefficients
        p = ModularPolynomial(7, [-3, 8, -5, 12])
        self.assertEqual(p.coefficients, [4, 1, 2, 5])

        # Test normalization with very large coefficients
        p = ModularPolynomial(5, [1001, 1002, 1003])
        self.assertEqual(p.coefficients, [1, 2, 3])

    def test_init_invalid_modulus(self):
        """Test that invalid moduli raise appropriate errors"""
        with self.assertRaises(ValueError):
            ModularPolynomial(0, [1, 2, 3])
        with self.assertRaises(ValueError):
            ModularPolynomial(-5, [1, 2, 3])

    def test_str_representation(self):
        """Test string representation of polynomials"""
        test_cases = [
            (ModularPolynomial(5, []), "0 mod 5"),
            (ModularPolynomial(7, [0]), "0 mod 7"),
            (ModularPolynomial(3, [1]), "1 mod 3"),
            (ModularPolynomial(5, [0, 1]), "x mod 5"),
            (ModularPolynomial(7, [1, 1]), "x + 1 mod 7"),
            (ModularPolynomial(11, [1, 2, 1]), "x^2 + 2x + 1 mod 11"),
            (ModularPolynomial(13, [0, 0, 1]), "x^2 mod 13"),
            (ModularPolynomial(17, [1, 0, 3]), "3x^2 + 1 mod 17")
        ]

        for poly, expected in test_cases:
            self.assertEqual(str(poly), expected)

    def test_str_representation_edge_cases(self):
        """Test string representation edge cases"""
        test_cases = [
            (ModularPolynomial(5, [-1]), "4 mod 5"),  # Negative constant
            (ModularPolynomial(5, [0, -1]), "4x mod 5"),  # Negative coefficient
            (ModularPolynomial(5, [0, 0, -1]), "4x^2 mod 5"),  # Negative leading coefficient
            (ModularPolynomial(5, [1, 0, 0, 1]), "x^3 + 1 mod 5"),  # Internal zeros
            (ModularPolynomial(5, [0, 0, 0, 1]), "x^3 mod 5")  # Leading term only
        ]
        for poly, expected in test_cases:
            self.assertEqual(str(poly), expected)

    def test_equality(self):
        """Test polynomial equality comparison"""
        # Same polynomials
        p1 = ModularPolynomial(5, [1, 2, 3])
        p2 = ModularPolynomial(5, [1, 2, 3])
        self.assertEqual(p1, p2)

        # Different coefficients
        p3 = ModularPolynomial(5, [1, 2, 4])
        self.assertNotEqual(p1, p3)

        # Different moduli
        p4 = ModularPolynomial(7, [1, 2, 3])
        self.assertNotEqual(p1, p4)

        # Same polynomial with trailing zeros
        p5 = ModularPolynomial(5, [1, 2, 3, 0, 0])
        self.assertEqual(p1, p5)

        # Comparison with non-ModularPolynomial
        self.assertNotEqual(p1, [1, 2, 3])
        self.assertNotEqual(p1, "polynomial")

    def test_get_degree(self):
        """Test polynomial degree calculation"""
        test_cases = [
            (ModularPolynomial(5, []), 0),  # zero polynomial
            (ModularPolynomial(5, [1]), 0),  # constant
            (ModularPolynomial(5, [1, 2]), 1),  # linear
            (ModularPolynomial(5, [1, 0, 3]), 2),  # quadratic
            (ModularPolynomial(5, [1, 2, 3, 0]), 2),  # trailing zeros removed
        ]

        for poly, expected_degree in test_cases:
            self.assertEqual(poly.get_degree(), expected_degree)

    def test_get_lead_coefficient(self):
        """Test leading coefficient retrieval"""
        test_cases = [
            (ModularPolynomial(5, []), 0),  # zero polynomial
            (ModularPolynomial(5, [2]), 2),  # constant
            (ModularPolynomial(5, [1, 3]), 3),  # linear
            (ModularPolynomial(5, [1, 2, 4]), 4),  # quadratic
            (ModularPolynomial(7, [1, 2, 6]), 6),  # not reduced
        ]

        for poly, expected_coeff in test_cases:
            self.assertEqual(poly.get_lead_coefficient(), expected_coeff)

    def test_get_copy(self):
        """Test polynomial copying"""
        original = ModularPolynomial(5, [1, 2, 3])
        copy = original.get_copy()

        # Test equality
        self.assertEqual(original, copy)

        # Test independence (deep copy)
        copy.coefficients[0] = 4
        self.assertNotEqual(original, copy)
        self.assertEqual(original.coefficients[0], 1)

    def test_get_negative(self):
        """Test polynomial negation"""
        test_cases = [
            # (original polynomial, expected negation)
            (ModularPolynomial(5, []), ModularPolynomial(5, [0])),  # zero
            (ModularPolynomial(5, [1]), ModularPolynomial(5, [4])),  # constant
            (ModularPolynomial(5, [1, 2]), ModularPolynomial(5, [4, 3])),  # linear
            (ModularPolynomial(7, [1, 2, 3]), ModularPolynomial(7, [6, 5, 4])),  # quadratic
        ]

        for poly, expected in test_cases:
            self.assertEqual(poly.get_negative(), expected)
            # Test double negation
            self.assertEqual(poly.get_negative().get_negative(), poly)

    def test_is_zero(self):
        """Test zero polynomial detection"""
        # Zero polynomials
        self.assertTrue(ModularPolynomial(5, []).is_zero())
        self.assertTrue(ModularPolynomial(5, [0]).is_zero())
        self.assertTrue(ModularPolynomial(5, [0, 0, 0]).is_zero())

        # Non-zero polynomials
        self.assertFalse(ModularPolynomial(5, [1]).is_zero())
        self.assertFalse(ModularPolynomial(5, [0, 1]).is_zero())
        self.assertFalse(ModularPolynomial(5, [1, 0, 0]).is_zero())

    def test_is_constant(self):
        """Test constant polynomial detection"""
        # Constant polynomials
        self.assertTrue(ModularPolynomial(5, []).is_constant())
        self.assertTrue(ModularPolynomial(5, [0]).is_constant())
        self.assertTrue(ModularPolynomial(5, [3]).is_constant())

        # Non-constant polynomials
        self.assertFalse(ModularPolynomial(5, [1, 2]).is_constant())
        self.assertFalse(ModularPolynomial(5, [0, 1]).is_constant())
        self.assertFalse(ModularPolynomial(5, [1, 0, 3]).is_constant())

    def test_is_one(self):
        """Test unit polynomial detection"""
        # Unit polynomials
        self.assertTrue(ModularPolynomial(5, [1]).is_one())
        self.assertTrue(ModularPolynomial(7, [1]).is_one())

        # Non-unit polynomials
        self.assertFalse(ModularPolynomial(5, []).is_one())
        self.assertFalse(ModularPolynomial(5, [0]).is_one())
        self.assertFalse(ModularPolynomial(5, [2]).is_one())
        self.assertFalse(ModularPolynomial(5, [1, 1]).is_one())
        self.assertFalse(ModularPolynomial(5, [0, 1]).is_one())

    def test_evaluate(self):
        """Test polynomial evaluation"""
        # Test zero polynomial
        zero_poly = ModularPolynomial(5, [])
        self.assertEqual(zero_poly.evaluate(3), 0)
        self.assertEqual(zero_poly.evaluate(10), 0)  # Large input

        # Test constant polynomial
        const_poly = ModularPolynomial(7, [3])  # 3 mod 7
        self.assertEqual(const_poly.evaluate(0), 3)
        self.assertEqual(const_poly.evaluate(5), 3)

        # Test linear polynomial
        linear_poly = ModularPolynomial(5, [2, 3])  # 3x + 2 mod 5
        test_cases_linear = [
            (0, 2),  # 3(0) + 2 = 2 mod 5
            (1, 0),  # 3(1) + 2 = 5 = 0 mod 5
            (2, 3),  # 3(2) + 2 = 8 = 3 mod 5
            (6, 0),  # 3(6) + 2 = 20 = 0 mod 5
        ]
        for x, expected in test_cases_linear:
            self.assertEqual(linear_poly.evaluate(x), expected)

        # Test quadratic polynomial
        quad_poly = ModularPolynomial(7, [1, 2, 3])  # 3x^2 + 2x + 1 mod 7
        test_cases_quad = [
            (0, 1),  # 3(0)^2 + 2(0) + 1 = 1 mod 7
            (1, 6),  # 3(1)^2 + 2(1) + 1 = 6 mod 7
            (2, 3),  # 3(2)^2 + 2(2) + 1 = 17 = 3 mod 7
            (8, 6),  # Should give same result as x=1 due to modular arithmetic
        ]
        for x, expected in test_cases_quad:
            self.assertEqual(quad_poly.evaluate(x), expected)

        # Test higher degree polynomial
        cubic_poly = ModularPolynomial(11, [1, 2, 3, 4])  # 4x^3 + 3x^2 + 2x + 1 mod 11
        test_cases_cubic = [
            (0, 1),  # 4(0)^3 + 3(0)^2 + 2(0) + 1 = 1 mod 11
            (1, 10),  # 4(1)^3 + 3(1)^2 + 2(1) + 1 = 10 mod 11
            (2, 5),  # 4(8) + 3(4) + 2(2) + 1 = 5 mod 11
        ]
        for x, expected in test_cases_cubic:
            self.assertEqual(cubic_poly.evaluate(x), expected)

    def test_evaluate_edge_cases(self):
        """Test polynomial evaluation edge cases"""
        # Test evaluation with negative inputs
        poly = ModularPolynomial(5, [1, 1])  # x + 1 mod 5
        self.assertEqual(poly.evaluate(-1), 0)  # (-1) + 1 = 0 mod 5

        # Test evaluation with very large inputs
        self.assertEqual(poly.evaluate(1000), poly.evaluate(0))  # Should wrap around

        # Test evaluation of polynomial with negative coefficients
        poly = ModularPolynomial(7, [-2, -3])  # 4x + 5 mod 7
        self.assertEqual(poly.evaluate(2), 6)  # 4(2) + 5 = 13 = 6 mod 7

    def test_add_to(self):
        """Test polynomial addition"""
        # Test addition of equal degree polynomials
        p1 = ModularPolynomial(5, [1, 2, 3])  # 3x^2 + 2x + 1 mod 5
        p2 = ModularPolynomial(5, [2, 1, 2])  # 2x^2 + x + 2 mod 5
        result = p1.add_to(p2)
        self.assertEqual(result.coefficients, [3, 3])  # (3x^2 + 2x + 1) + (2x^2 + x + 2) = 3x + 3 mod 5

        # Test addition of different degree polynomials
        p3 = ModularPolynomial(5, [1, 2])  # 2x + 1 mod 5
        p4 = ModularPolynomial(5, [3, 4, 1])  # x^2 + 4x + 3 mod 5
        result = p3.add_to(p4)
        self.assertEqual(result.coefficients, [4, 1, 1])  # (2x + 1) + (x^2 + 4x + 3) = x^2 + x + 4 mod 5

        # Test addition with zero polynomial
        zero = ModularPolynomial(5, [])
        result = p1.add_to(zero)
        self.assertEqual(result, p1)
        result = zero.add_to(p1)
        self.assertEqual(result, p1)

        # Test addition with different moduli
        p5 = ModularPolynomial(7, [1, 2, 3])
        with self.assertRaises(ValueError):
            p1.add_to(p5)

        # Test addition that results in coefficient cancellation
        p6 = ModularPolynomial(5, [1, 2, 2])  # 2x^2 + 2x + 1 mod 5
        p7 = ModularPolynomial(5, [0, 0, 3])  # 3x^2 mod 5
        result = p6.add_to(p7)
        self.assertEqual(result.coefficients, [1, 2])  # Leading term cancels to 0

    def test_add_to_with_negative(self):
        """Test polynomial subtraction using add_to with negative flag"""
        # Test basic subtraction
        p1 = ModularPolynomial(5, [1, 2, 3])  # 3x^2 + 2x + 1 mod 5
        p2 = ModularPolynomial(5, [2, 1, 2])  # 2x^2 + x + 2 mod 5
        result = p1.add_to(p2, negative=True)
        self.assertEqual(result.coefficients, [4, 1, 1])  # (3x^2 + 2x + 1) - (2x^2 + x + 2) = x^2 + x + 4 mod 5

        # Test subtraction with different degrees
        p3 = ModularPolynomial(5, [1, 2])  # 2x + 1 mod 5
        p4 = ModularPolynomial(5, [3, 4, 1])  # x^2 + 4x + 3 mod 5
        result = p3.add_to(p4, negative=True)
        self.assertEqual(result.coefficients, [3, 3, 4])  # (2x + 1) - (x^2 + 4x + 3) = 4x^2 + 3x + 3 mod 5

        # Test subtraction with zero
        zero = ModularPolynomial(5, [])
        result = p1.add_to(zero, negative=True)
        self.assertEqual(result, p1)
        result = zero.add_to(p1, negative=True)
        self.assertEqual(result, p1.get_negative())

        # Verify p - p = 0 for any polynomial p
        result = p1.add_to(p1, negative=True)
        self.assertTrue(result.is_zero())

    def test_add_one(self):
        """Test adding one to polynomial"""
        # Test adding one to zero polynomial
        zero = ModularPolynomial(5, [])
        result = zero.add_one()
        self.assertEqual(result.coefficients, [1])  # 0 + 1 = 1 mod 5

        # Test adding one to constant polynomial
        const = ModularPolynomial(5, [4])  # 4 mod 5
        result = const.add_one()
        self.assertEqual(result.coefficients, [0])  # 4 + 1 = 0 mod 5

        # Test adding one to non-constant polynomial
        poly = ModularPolynomial(5, [4, 2, 1])  # x^2 + 2x + 4 mod 5
        result = poly.add_one()
        self.assertEqual(result.coefficients, [0, 2, 1])  # x^2 + 2x + 4 + 1 = x^2 + 2x + 0 mod 5

    def test_subtract_from(self):
        """Test polynomial subtraction using subtract_from"""
        # Test basic subtraction
        p1 = ModularPolynomial(5, [1, 2, 3])  # 3x^2 + 2x + 1 mod 5
        p2 = ModularPolynomial(5, [2, 1, 2])  # 2x^2 + x + 2 mod 5
        result = p1.subtract_from(p2)  # (2x^2 + x + 2) - (3x^2 + 2x + 1)
        self.assertEqual(result.coefficients, [1, 4, 4])  # 4x^2 + 4x + 1 mod 5

        # Verify that (p2 - p1) = -(p1 - p2)
        result2 = p2.subtract_from(p1)
        expected = result.get_negative()
        self.assertEqual(result2, expected)

        # Test subtraction with zero polynomial
        zero = ModularPolynomial(5, [])
        result = p1.subtract_from(zero)
        self.assertEqual(result, p1.get_negative())
        result = zero.subtract_from(p1)
        self.assertEqual(result, p1)

        # Test a - a = 0 for any polynomial a
        result = p1.subtract_from(p1)
        self.assertTrue(result.is_zero())

        # Test with different moduli
        p3 = ModularPolynomial(7, [1, 2, 3])
        with self.assertRaises(ValueError):
            p1.subtract_from(p3)

    def test_product_with(self):
        """Test polynomial multiplication"""
        # Test multiplication of constant polynomials
        p1 = ModularPolynomial(5, [2])  # 2 mod 5
        p2 = ModularPolynomial(5, [3])  # 3 mod 5
        result = p1.product_with(p2)
        self.assertEqual(result.coefficients, [1])  # 2 * 3 = 1 mod 5

        # Test multiplication by zero
        zero = ModularPolynomial(5, [])
        result = p1.product_with(zero)
        self.assertTrue(result.is_zero())
        result = zero.product_with(p1)
        self.assertTrue(result.is_zero())

        # Test multiplication by one
        one = ModularPolynomial(5, [1])
        result = p1.product_with(one)
        self.assertEqual(result, p1)

        # Test multiplication of linear polynomials
        p3 = ModularPolynomial(5, [1, 2])  # 2x + 1 mod 5
        p4 = ModularPolynomial(5, [3, 1])  # x + 3 mod 5
        result = p3.product_with(p4)
        # (2x + 1)(x + 3) = 2x^2 + 6x + x + 3 = 2x^2 + 2x + 3 mod 5
        self.assertEqual(result.coefficients, [3, 2, 2])

        # Test multiplication of quadratic by linear
        p5 = ModularPolynomial(5, [1, 0, 1])  # x^2 + 1 mod 5
        p6 = ModularPolynomial(5, [0, 1])  # x mod 5
        result = p5.product_with(p6)
        # (x^2 + 1)(x) = x^3 + x mod 5
        self.assertEqual(result.coefficients, [0, 1, 0, 1])

        # Test multiplication with modular reduction of coefficients
        p7 = ModularPolynomial(5, [2, 3])  # 3x + 2 mod 5
        p8 = ModularPolynomial(5, [4, 2])  # 2x + 4 mod 5
        result = p7.product_with(p8)
        # (3x + 2)(2x + 4) = 6x^2 + 16x + 8 = x^2 + 1x + 3 mod 5
        self.assertEqual(result.coefficients, [3, 1, 1])

        # Test multiplication with different moduli
        p9 = ModularPolynomial(7, [1, 1])
        with self.assertRaises(ValueError):
            p1.product_with(p9)

        # Test associative property: (a * b) * c = a * (b * c)
        a = ModularPolynomial(5, [1, 2])  # 2x + 1 mod 5
        b = ModularPolynomial(5, [3, 1])  # x + 3 mod 5
        c = ModularPolynomial(5, [2, 1, 1])  # x^2 + x + 2 mod 5
        result1 = a.product_with(b).product_with(c)
        result2 = a.product_with(b.product_with(c))
        self.assertEqual(result1, result2)

        # Test commutative property: a * b = b * a
        result1 = a.product_with(b)
        result2 = b.product_with(a)
        self.assertEqual(result1, result2)

        # Test distributive property: a * (b + c) = (a * b) + (a * c)
        result1 = a.product_with(b.add_to(c))
        result2 = a.product_with(b).add_to(a.product_with(c))
        self.assertEqual(result1, result2)

    def test_divided_by(self):
        """Test polynomial division"""
        # Test simple division with no remainder
        p1 = ModularPolynomial(5, [0, 0, 1])  # x^2 mod 5
        p2 = ModularPolynomial(5, [0, 1])  # x mod 5
        result = p1.divided_by(p2)
        self.assertEqual(result.quotient.coefficients, [0, 1])  # x mod 5
        self.assertTrue(result.remainder.is_zero())

        # Test division with remainder
        p3 = ModularPolynomial(5, [1, 1, 1])  # x^2 + x + 1 mod 5
        p4 = ModularPolynomial(5, [1, 1])  # x + 1 mod 5
        result = p3.divided_by(p4)
        # (x^2 + x + 1) = (x + 1)(x) + 1
        self.assertEqual(result.quotient.coefficients, [0, 1])  # x mod 5
        self.assertEqual(result.remainder.coefficients, [1])  # 1 mod 5

        # Test division by constant
        p5 = ModularPolynomial(5, [2, 3, 4])  # 4x^2 + 3x + 2 mod 5
        p6 = ModularPolynomial(5, [2])  # 2 mod 5
        result = p5.divided_by(p6)
        # (4x^2 + 3x + 2) = 2(2x^2 + 4x + 1)
        self.assertEqual(result.quotient.coefficients, [1, 4, 2])  # 2x^2 + 4x + 1 mod 5
        self.assertTrue(result.remainder.is_zero())

        # Test division where inverse of leading coefficient is needed
        p7 = ModularPolynomial(5, [1, 2])  # 2x + 1 mod 5
        p8 = ModularPolynomial(5, [0, 3])  # 3x mod 5
        result = p7.divided_by(p8)
        # (2x + 1) = (3x)(4) + 1, where 2 = 3^(-1) mod 5
        self.assertEqual(result.quotient.coefficients, [4])  # 2 mod 5
        self.assertEqual(result.remainder.coefficients, [1])  # 1 mod 5

        # Test division by linear term
        p9 = ModularPolynomial(5, [1, 0, 1])  # x^2 + 1 mod 5
        p10 = ModularPolynomial(5, [2, 1])  # x + 2 mod 5
        result = p9.divided_by(p10)
        self.assertEqual(len(result.quotient.coefficients), 2)  # Should be linear
        # Verify: original = (divisor × quotient) + remainder
        recomputed = p10.product_with(result.quotient).add_to(result.remainder)
        self.assertEqual(recomputed, p9)

        # Test division by higher degree polynomial
        p11 = ModularPolynomial(5, [1, 1])  # x + 1 mod 5
        p12 = ModularPolynomial(5, [1, 0, 1])  # x^2 + 1 mod 5
        result = p11.divided_by(p12)
        self.assertTrue(result.quotient.is_zero())  # Quotient should be 0
        self.assertEqual(result.remainder, p11)  # Remainder should be original polynomial

        # Test error conditions
        # Different moduli
        p13 = ModularPolynomial(7, [1, 1])
        with self.assertRaises(ValueError):
            p1.divided_by(p13)

        # Division by zero
        zero = ModularPolynomial(5, [])
        with self.assertRaises(ValueError):
            p1.divided_by(zero)

        # Verify division properties
        # For any polynomials a and b (b ≠ 0), there exist unique q and r such that:
        # a = bq + r, where degree(r) < degree(b) or r = 0
        test_pairs = [
            (ModularPolynomial(5, [1, 2, 3]), ModularPolynomial(5, [1, 1])),
            (ModularPolynomial(5, [4, 0, 1]), ModularPolynomial(5, [2, 1])),
            (ModularPolynomial(5, [1, 1, 1, 1]), ModularPolynomial(5, [1, 0, 1]))
        ]
        for dividend, divisor in test_pairs:
            result = dividend.divided_by(divisor)
            # Verify degree of remainder < degree of divisor
            if not result.remainder.is_zero():
                self.assertLess(result.remainder.get_degree(), divisor.get_degree())
            # Verify division equation: dividend = (divisor × quotient) + remainder
            recomputed = divisor.product_with(result.quotient).add_to(result.remainder)
            self.assertEqual(recomputed, dividend)


    def test_division_edge_cases(self):
        """Test polynomial division edge cases"""
        # Division where intermediate steps produce higher degree terms
        p1 = ModularPolynomial(5, [1, 0, 0, 1])  # x^3 + 1
        p2 = ModularPolynomial(5, [2, 1])  # x + 2
        result = p1.divided_by(p2)
        recomputed = p2.product_with(result.quotient).add_to(result.remainder)
        self.assertEqual(recomputed, p1)


    def test_mathematical_properties(self):
        """Test various mathematical properties and identities"""
        a = ModularPolynomial(5, [1, 2])  # 2x + 1
        b = ModularPolynomial(5, [3, 1])  # x + 3
        c = ModularPolynomial(5, [2, 1, 1])  # x^2 + x + 2

        # Distributive property with subtraction
        left = a.product_with(b.subtract_from(c))
        right = a.product_with(b).subtract_from(a.product_with(c))
        self.assertEqual(left, right)

        # Zero property with multiplication and division
        zero = ModularPolynomial(5, [])
        self.assertEqual(a.product_with(zero), zero)
        self.assertEqual(zero.product_with(a), zero)

    def test_check_if_primitive(self):
        """Test primitive element checking in finite fields"""
        # Test known primitive elements
        self.assertTrue(check_if_primitive(2, 5))  # 2 is primitive mod 5
        self.assertTrue(check_if_primitive(3, 7))  # 3 is primitive mod 7

        # Test non-primitive elements
        self.assertFalse(check_if_primitive(1, 5))  # 1 is never primitive
        self.assertFalse(check_if_primitive(4, 7))  # 4 is not primitive mod 7

        # Test all elements in small fields
        primitives_mod5 = [x for x in range(1, 5) if check_if_primitive(x, 5)]
        self.assertEqual(set(primitives_mod5), {2, 3})  # Known primitive elements mod 5

        primitives_mod7 = [x for x in range(1, 7) if check_if_primitive(x, 7)]
        self.assertEqual(set(primitives_mod7), {3, 5})  # Known primitive elements mod 7

    def test_compute_large_exponent_of_x(self):
        """Test computation of x raised to large powers modulo a polynomial"""
        # Test with simple modulus polynomial x^2 + 1
        mod_poly = ModularPolynomial(3, [1, 0, 1])  # x^2 + 1 mod 3

        # Test small powers
        result = compute_large_exponent_of_x(1, mod_poly)
        self.assertEqual(result, ModularPolynomial(3, [0, 1]))  # x

        result = compute_large_exponent_of_x(2, mod_poly)
        self.assertEqual(result, ModularPolynomial(3, [2, 0]))  # -1 mod 3

        # Test power that should cycle back to x
        result = compute_large_exponent_of_x(8, mod_poly)
        self.assertEqual(result, ModularPolynomial(3, [1]))  # x

        # Test with different modulus polynomial
        mod_poly2 = ModularPolynomial(2, [1, 1, 1])  # x^2 + x + 1 mod 2
        result = compute_large_exponent_of_x(3, mod_poly2)
        self.assertEqual(result, ModularPolynomial(2, [1]))  # x + 1 mod 2

    def test_check_if_irreducible(self):
        """Test irreducibility checking of polynomials"""
        # Test known irreducible polynomials
        self.assertTrue(check_if_irreducible(ModularPolynomial(2, [1, 1])))  # x + 1 mod 2
        self.assertTrue(check_if_irreducible(ModularPolynomial(2, [1, 1, 1])))  # x^2 + x + 1 mod 2

        # Test known reducible polynomials
        self.assertFalse(check_if_irreducible(ModularPolynomial(2, [0])))  # 0 mod 2
        self.assertFalse(check_if_irreducible(ModularPolynomial(2, [1, 0, 1])))  # x^2 + 1 mod 2 = (x+1)(x+1)

        # Test special cases
        self.assertTrue(check_if_irreducible(ModularPolynomial(2, [1])))  # Constant non-zero polynomial
        self.assertTrue(check_if_irreducible(ModularPolynomial(3, [1, 1])))  # Linear polynomial

        # Test higher degree cases
        self.assertTrue(check_if_irreducible(ModularPolynomial(2, [1, 1, 0, 1])))  # x^3 + x + 1 mod 2

    def test_find_irreducible(self):
        """Test finding irreducible polynomials of given degree"""
        # Test degree 1 cases
        poly = find_irreducible(2, 1)
        self.assertEqual(poly, ModularPolynomial(2, [0, 1]))
        self.assertTrue(check_if_irreducible(poly))

        # Test degree 2 cases
        poly = find_irreducible(2, 2)
        self.assertEqual(poly.get_degree(), 2)
        self.assertTrue(check_if_irreducible(poly))

        # Test degree 3 cases
        poly = find_irreducible(2, 3)
        self.assertEqual(poly.get_degree(), 3)
        self.assertTrue(check_if_irreducible(poly))

        # Test special cases mentioned in the code
        poly = find_irreducible(2, 8)
        self.assertEqual(poly, ModularPolynomial(2, [1, 1, 0, 0, 0, 0, 1, 1, 1]))
        self.assertTrue(check_if_irreducible(poly))

    def setUp(self):
        """Set up some common calculators for testing"""
        # F₂² calculator
        self.calc_f4 = FiniteFieldCalculator(2, 2)
        # F₂³ calculator
        self.calc_f8 = FiniteFieldCalculator(2, 3)
        # F₃² calculator
        self.calc_f9 = FiniteFieldCalculator(3, 2)

    def test_initialization(self):
        """Test calculator initialization with different fields"""
        # Test that initialization creates appropriate irreducible polynomials
        self.assertEqual(self.calc_f4.prime_modulus, 2)
        self.assertTrue(self.calc_f4.polynomial_modulus.get_degree() == 2)

        self.assertEqual(self.calc_f8.prime_modulus, 2)
        self.assertTrue(self.calc_f8.polynomial_modulus.get_degree() == 3)

        self.assertEqual(self.calc_f9.prime_modulus, 3)
        self.assertTrue(self.calc_f9.polynomial_modulus.get_degree() == 2)

        # Test invalid initializations
        with self.assertRaises(ValueError):
            FiniteFieldCalculator(0, 1)  # Invalid prime
        with self.assertRaises(ValueError):
            FiniteFieldCalculator(4, 1)  # Non-prime modulus

    def test_multiplicative_inverse(self):
        """Test finding multiplicative inverses in finite fields"""
        # Test in F₄
        poly = ModularPolynomial(2, [1, 1])  # x + 1
        inv = self.calc_f4.find_multiplicative_inverse(poly)
        # Verify inv * poly ≡ 1 (mod polynomial_modulus)
        product = poly.product_with(inv)
        result = product.divided_by(self.calc_f4.polynomial_modulus).remainder
        self.assertTrue(result.is_one())

        # Test in F₉
        poly = ModularPolynomial(3, [1, 1])  # x + 1
        inv = self.calc_f9.find_multiplicative_inverse(poly)
        product = poly.product_with(inv)
        result = product.divided_by(self.calc_f9.polynomial_modulus).remainder
        self.assertTrue(result.is_one())

        # Test inverting 1
        poly = ModularPolynomial(2, [1])  # 1 in F₄
        inv = self.calc_f4.find_multiplicative_inverse(poly)
        self.assertTrue(inv.is_one())

        # Test inverting elements with no inverse
        with self.assertRaises(ValueError):
            self.calc_f4.find_multiplicative_inverse(ModularPolynomial(2, [0]))  # Zero has no inverse

    def test_addition(self):
        """Test addition in finite fields"""
        # Test in F₄
        result = self.calc_f4.handle_operation([1, 0], [0, 1], calculator_engine.FieldOperation.ADD)  # x + 1
        self.assertEqual(result, ModularPolynomial(2, [1, 1]))

        # Test in F₉
        result = self.calc_f9.handle_operation([1, 1], [2, 1], calculator_engine.FieldOperation.ADD)  # (x+1) + (x+2)
        self.assertEqual(result, ModularPolynomial(3, [0, 2]))  # 2x

        # Test adding zero
        result = self.calc_f4.handle_operation([1, 1], [0], calculator_engine.FieldOperation.ADD)
        self.assertEqual(result, ModularPolynomial(2, [1, 1]))

        # Test self-addition
        result = self.calc_f4.handle_operation([1, 1], [1, 1], calculator_engine.FieldOperation.ADD)
        self.assertEqual(result, ModularPolynomial(2, [0]))  # In F₂, x+x=0

    def test_subtraction(self):
        """Test subtraction in finite fields"""
        # In F₂, addition and subtraction are the same
        result1 = self.calc_f4.handle_operation([1, 1], [1, 0], calculator_engine.FieldOperation.ADD)
        result2 = self.calc_f4.handle_operation([1, 1], [1, 0], calculator_engine.FieldOperation.SUBTRACT)
        self.assertEqual(result1, result2)

        # Test in F₉
        result = self.calc_f9.handle_operation([1, 1], [2, 1], calculator_engine.FieldOperation.SUBTRACT)
        self.assertEqual(result, ModularPolynomial(3, [2, 0]))  # Should be 2

        # Test self-subtraction
        result = self.calc_f4.handle_operation([1, 1], [1, 1], calculator_engine.FieldOperation.SUBTRACT)
        self.assertTrue(result.is_zero())


    def test_multiplication(self):
        """Test multiplication in finite fields"""
        # Test in F₄
        result = self.calc_f4.handle_operation([1, 1], [1, 1], calculator_engine.FieldOperation.MULTIPLY)  # (x+1)(x+1)
        # Result should be reduced modulo the irreducible polynomial
        self.assertTrue(result.get_degree() < self.calc_f4.polynomial_modulus.get_degree())

        # Test multiplication by 1
        result = self.calc_f4.handle_operation([1, 1], [1], calculator_engine.FieldOperation.MULTIPLY)
        self.assertEqual(result, ModularPolynomial(2, [1, 1]))

        # Test multiplication by 0
        result = self.calc_f4.handle_operation([1, 1], [0], calculator_engine.FieldOperation.MULTIPLY)
        self.assertTrue(result.is_zero())

    def test_division(self):
        """Test division in finite fields"""
        # Test division by 1
        result = self.calc_f4.handle_operation([1, 1], [1], calculator_engine.FieldOperation.DIVIDE)
        self.assertEqual(result, ModularPolynomial(2, [1, 1]))

        # Test self-division
        result = self.calc_f4.handle_operation([1, 1], [1, 1], calculator_engine.FieldOperation.DIVIDE)
        self.assertTrue(result.is_one())

        # Test division by 0
        with self.assertRaises(ValueError):
            self.calc_f4.handle_operation([1, 1], [0], calculator_engine.FieldOperation.DIVIDE)

        # Test division in F₉
        poly1 = [1, 1]  # x + 1
        poly2 = [2, 1]  # x + 2
        result = self.calc_f9.handle_operation(poly1, poly2, calculator_engine.FieldOperation.DIVIDE)
        # Verify result by multiplying back
        check = self.calc_f9.handle_operation(result.coefficients, poly2, calculator_engine.FieldOperation.MULTIPLY)
        self.assertEqual(check, ModularPolynomial(3, poly1))

    def test_field_axioms(self):
        """Test that field axioms hold"""
        # Test associativity of addition
        a = [1, 1]  # x + 1
        b = [1, 0]  # x
        c = [0, 1]  # 1

        # (a + b) + c = a + (b + c)
        result1 = self.calc_f4.handle_operation(
            self.calc_f4.handle_operation(a, b, calculator_engine.FieldOperation.ADD).coefficients,
            c, calculator_engine.FieldOperation.ADD
        )
        result2 = self.calc_f4.handle_operation(
            a,
            self.calc_f4.handle_operation(b, c, calculator_engine.FieldOperation.ADD).coefficients,
            calculator_engine.FieldOperation.ADD
        )
        self.assertEqual(result1, result2)

        # Test distributive property
        # a * (b + c) = (a * b) + (a * c)
        left_side = self.calc_f4.handle_operation(
            a,
            self.calc_f4.handle_operation(b, c, calculator_engine.FieldOperation.ADD).coefficients,
            calculator_engine.FieldOperation.MULTIPLY
        )
        right_side = self.calc_f4.handle_operation(
            self.calc_f4.handle_operation(a, b, calculator_engine.FieldOperation.MULTIPLY).coefficients,
            self.calc_f4.handle_operation(a, c, calculator_engine.FieldOperation.MULTIPLY).coefficients,
            calculator_engine.FieldOperation.ADD
        )
        self.assertEqual(left_side, right_side)

    @staticmethod
    def is_prime(n):
        """Helper function to check if a number is prime"""
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

    def generate_random_field(self):
        """Generate a random finite field calculator with prime_modulus <= 101 and dim <= 12"""
        # Generate list of primes up to 101
        primes = [n for n in range(2, 102) if self.is_prime(n)]
        prime_modulus = random.choice(primes)
        dim = random.randint(1, 12)
        return FiniteFieldCalculator(prime_modulus, dim)

    def generate_random_polynomial(self, calculator):
        """Generate a random non-zero polynomial in the field"""
        degree = random.randint(0, calculator.polynomial_modulus.get_degree() - 1)
        coeffs = [random.randint(0, calculator.prime_modulus - 1) for _ in range(degree + 1)]
        # Ensure we don't get a zero polynomial
        while all(c == 0 for c in coeffs):
            coeffs = [random.randint(0, calculator.prime_modulus - 1) for _ in range(degree + 1)]
        return coeffs



    def test_extensive_field_properties(self):
        """Comprehensive stress test of field properties across many fields and polynomials"""
        # Set random seed for reproducibility
        random.seed(13)


        # Track statistics
        total_operations = 0
        fields_tested = []

        for prime_modulus in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]:
            for dim in range(1, 13):
                polynomials_per_field = prime_modulus * dim

                calculator = FiniteFieldCalculator(prime_modulus, dim)

                fields_tested.append((prime_modulus, dim))
                print(f"\nTesting field:")
                print(f"Prime modulus: {calculator.prime_modulus}")
                print(f"Extension degree: {calculator.polynomial_modulus.get_degree()}")

                # Generate more polynomials of varying degrees
                polynomials = []
                for _ in range(polynomials_per_field):
                    # Vary polynomial degrees more widely
                    degree = random.randint(0, calculator.polynomial_modulus.get_degree() - 1)
                    # Sometimes generate sparse polynomials
                    if random.random() < 0.2:  # 20% chance of sparse polynomial
                        num_terms = random.randint(1, degree + 1)
                        coeffs = [0] * (degree + 1)
                        for _ in range(num_terms):
                            pos = random.randint(0, degree)
                            coeffs[pos] = random.randint(1, calculator.prime_modulus - 1)
                    else:
                        coeffs = [random.randint(0, calculator.prime_modulus - 1) for _ in range(degree + 1)]

                    # Ensure non-zero polynomial
                    while all(c == 0 for c in coeffs):
                        coeffs = [random.randint(0, calculator.prime_modulus - 1) for _ in range(degree + 1)]
                    polynomials.append(coeffs)

                # Add some special polynomials to test edge cases
                if dim == 1:
                    special_polynomials = [[1]]
                else:
                    special_polynomials = [
                        [1],  # 1
                        [0, 1],  # x
                        [1] * calculator.polynomial_modulus.get_degree(),  # all ones
                        [1 if i == 0 or i == calculator.polynomial_modulus.get_degree() - 1 else 0
                         for i in range(calculator.polynomial_modulus.get_degree())]  # terms only at ends
                    ]
                polynomials.extend(special_polynomials)

                # Test field properties with all polynomial combinations
                for i in range(5):
                    for j in range(5):
                        for k in range(5):
                            a = random.choice(polynomials)
                            b = random.choice(polynomials)
                            c = random.choice(polynomials)

                            # Test associativity of addition: (a + b) + c = a + (b + c)
                            sum1 = calculator.handle_operation(
                                calculator.handle_operation(a, b, calculator_engine.FieldOperation.ADD).coefficients,
                                c, calculator_engine.FieldOperation.ADD
                            )
                            sum2 = calculator.handle_operation(
                                a,
                                calculator.handle_operation(b, c, calculator_engine.FieldOperation.ADD).coefficients,
                                calculator_engine.FieldOperation.ADD
                            )
                            self.assertEqual(sum1, sum2,
                                             f"Addition associativity failed in field F_{prime_modulus}^{dim}")
                            total_operations += 2

                            # Test commutativity of addition: a + b = b + a
                            sum1 = calculator.handle_operation(a, b, calculator_engine.FieldOperation.ADD)
                            sum2 = calculator.handle_operation(b, a, calculator_engine.FieldOperation.ADD)
                            self.assertEqual(sum1, sum2,
                                             f"Addition commutativity failed in field F_{prime_modulus}^{dim}")
                            total_operations += 2

                            # Test distributive property: a * (b + c) = (a * b) + (a * c)
                            left = calculator.handle_operation(
                                a,
                                calculator.handle_operation(b, c, calculator_engine.FieldOperation.ADD).coefficients,
                                calculator_engine.FieldOperation.MULTIPLY
                            )
                            right = calculator.handle_operation(
                                calculator.handle_operation(a, b, calculator_engine.FieldOperation.MULTIPLY).coefficients,
                                calculator.handle_operation(a, c, calculator_engine.FieldOperation.MULTIPLY).coefficients,
                                calculator_engine.FieldOperation.ADD
                            )
                            self.assertEqual(left, right,
                                             f"Distributive property failed in field F_{prime_modulus}^{dim}")
                            total_operations += 5

                            # Test commutativity of multiplication: a * b = b * a
                            prod1 = calculator.handle_operation(a, b, calculator_engine.FieldOperation.MULTIPLY)
                            prod2 = calculator.handle_operation(b, a, calculator_engine.FieldOperation.MULTIPLY)
                            self.assertEqual(prod1, prod2,
                                             f"Multiplication commutativity failed in field F_{prime_modulus}^{dim}")
                            total_operations += 2

                            # Test multiplicative inverse and division
                            try:
                                poly_a = ModularPolynomial(calculator.prime_modulus, a)
                                inv_a = calculator.find_multiplicative_inverse(poly_a)

                                # Test a * a^(-1) = 1
                                prod = calculator.handle_operation(a, inv_a.coefficients, calculator_engine.FieldOperation.MULTIPLY)
                                self.assertTrue(prod.is_one(),
                                                f"Multiplicative inverse property failed in field F_{prime_modulus}^{dim}")

                                # Test (a * b) / b = a
                                prod = calculator.handle_operation(a, b, calculator_engine.FieldOperation.MULTIPLY)
                                div = calculator.handle_operation(prod.coefficients, b, calculator_engine.FieldOperation.DIVIDE)
                                self.assertEqual(div, ModularPolynomial(calculator.prime_modulus, a),
                                                 f"Division property failed in field F_{prime_modulus}^{dim}")

                                total_operations += 3
                            except ValueError:
                                # Skip if polynomial has no inverse (i.e., is zero)
                                pass

                # Test to check if the polynomial modulus is reducible
                for p in polynomials:
                    modpoly = ModularPolynomial(calculator.prime_modulus, p)
                    if not modpoly.is_constant():
                        self.assertFalse(calculator.polynomial_modulus.divided_by(modpoly).remainder.is_zero(),
                                         f"Reducible Modulus found in field F_{prime_modulus}^{dim}")

        print("\nTest Summary:")
        print(f"Tested {len(fields_tested)} fields")
        print(f"Total operations performed: {total_operations}")


if __name__ == '__main__':
    unittest.main()
