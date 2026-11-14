"""Decide bounded-degree univariate real nonnegativity over exact rationals."""

from fractions import Fraction


class ArithmeticBudgetExceeded(ValueError):
    """An intermediate polynomial grew beyond the supported exact budget."""


def _trim(polynomial):
    while polynomial and not polynomial[-1]:
        polynomial.pop()
    if any(max(abs(c.numerator).bit_length(), c.denominator.bit_length()) > 8192 for c in polynomial):
        raise ArithmeticBudgetExceeded('univariate arithmetic exceeds the coefficient budget')
    return polynomial


def _scale(polynomial, factor):
    return _trim([coefficient * factor for coefficient in polynomial])


def _derivative(polynomial):
    return _trim([power * coefficient for power, coefficient in enumerate(polynomial) if power])


def _divide(dividend, divisor):
    remainder = list(dividend)
    quotient = [Fraction(0)] * max(0, len(dividend) - len(divisor) + 1)
    while remainder and len(remainder) >= len(divisor):
        offset = len(remainder) - len(divisor)
        factor = remainder[-1] / divisor[-1]
        quotient[offset] = factor
        for index, coefficient in enumerate(divisor):
            remainder[offset + index] -= factor * coefficient
        _trim(remainder)
    return _trim(quotient), remainder


def _quotient(dividend, divisor):
    quotient, remainder = _divide(dividend, divisor)
    if remainder:
        raise ValueError('unexpected remainder in exact square-free factorization')
    return quotient


def _gcd(left, right):
    while right:
        _, remainder = _divide(left, right)
        left, right = right, _scale(remainder, 1 / remainder[-1]) if remainder else []
    return _scale(left, 1 / left[-1]) if left else []


def _multiply(left, right):
    coefficients = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            coefficients[i + j] += a * b
    return _trim(coefficients)


def _odd_factor(monic):
    # Yun's square-free factorization in characteristic zero. At iteration m,
    # common and layer differ by precisely the factor of multiplicity m.
    repeated = _gcd(monic, _derivative(monic))
    layer = _quotient(monic, repeated)
    odd = [Fraction(1)]
    multiplicity = 1
    while len(layer) > 1:
        common = _gcd(layer, repeated)
        factor = _quotient(layer, common)
        if multiplicity % 2:
            odd = _multiply(odd, factor)
        layer = common
        repeated = _quotient(repeated, common)
        multiplicity += 1
    return odd


def _sturm_signs(square_free):
    sequence = [square_free]
    derivative = _derivative(square_free)
    if derivative:
        sequence.append(derivative)
    while len(sequence[-1]) > 1:
        _, remainder = _divide(sequence[-2], sequence[-1])
        if not remainder:
            raise ValueError('odd-multiplicity factor was not square free')
        # Only positive rescaling of a Sturm element preserves its signs.
        sequence.append(_scale(remainder, -1 / abs(remainder[-1])))
    positive = [1 if element[-1] > 0 else -1 for element in sequence]
    negative = [sign if len(element) % 2 else -sign for sign, element in zip(positive, sequence)]
    return negative, positive


def _variations(signs):
    return sum(left != right for left, right in zip(signs, signs[1:]))


def classify(polynomial):
    """Return the exact sign classification and the data independently replayed by verify.

    For positive leading coefficient and even degree, the polynomial has a
    negative value iff it has a real root of odd multiplicity. The sign is
    constant across even-multiplicity roots and changes across every odd one.
    """
    coefficients = [Fraction(0)] * (1 + max((powers[0] for powers in polynomial), default=0))
    for powers, coefficient in polynomial.items():
        coefficients[powers[0]] = coefficient
    if not _trim(coefficients):
        return True, {'criterion': 'zero_polynomial'}
    degree = len(coefficients) - 1
    leading = coefficients[-1]
    evidence = {'degree': degree, 'leading_coefficient': str(leading)}
    if degree % 2 or leading < 0:
        return False, dict(evidence, criterion='negative_tail')
    odd = _odd_factor(_scale(coefficients, 1 / leading))
    negative, positive = _sturm_signs(odd)
    count = _variations(negative) - _variations(positive)
    return count == 0, dict(evidence, criterion='odd_multiplicity_sturm',
                            odd_factor_ascending=[str(coefficient) for coefficient in odd],
                            signs_at_negative_infinity=negative, signs_at_positive_infinity=positive,
                            odd_multiplicity_real_roots=count)
