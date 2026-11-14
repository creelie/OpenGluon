"""Replay the rational arithmetic in the reciprocal coefficient bound."""

from fractions import Fraction


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def mobius_table(limit):
    values = [0, 1]
    for n in range(2, limit + 1):
        values.append(-sum(values[d] for d in divisors(n) if d < n))
    return values


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    limit = 160
    mobius = mobius_table(limit)
    reciprocal_tail_bound = sum((Fraction(1, k*k) for k in range(2, 6)), Fraction(1, 5))
    require(reciprocal_tail_bound < Fraction(2, 3), 'squarefree union bound fails')
    epsilon_max = Fraction(1, 100)
    require(Fraction(1, 1944) - Fraction(7, 6) * epsilon_max**2 >= Fraction(1, 3000),
            'numerical constant in the coefficient mass bound fails')

    for m in range(2, limit + 1):
        require(sum(mobius[n] ** 2 for n in range(1, m + 1)) >= Fraction(m, 3),
                'squarefree count fails')
        require(sum(sum(divisors(n)) for n in range(1, m + 1)) <= m*m,
                'divisor sum exceeds its budget')

    vectors = (
        {},
        {2: Fraction(1)},
        {2: Fraction(3, 2), 3: Fraction(1, 3), 4: Fraction(-2, 5)},
        {n: Fraction((-1)**n, n + 2) for n in range(2, 29)},
        {n: Fraction(-mobius[n]) for n in range(2, 65)},
    )
    total_checks = 0
    for coefficients in vectors:
        total_slope = sum((a/n for n, a in coefficients.items()), Fraction(0))
        error = [Fraction(0)] + [
            1 - sum((a * Fraction(q % n, n) for n, a in coefficients.items()), Fraction(0))
            for q in range(1, limit + 1)
        ]
        partial_error_squared = sum(error[q]**2 / (q*(q+1)) for q in range(1, limit + 1))
        for n in range(1, limit + 1):
            require(error[n] - error[n-1] == (n == 1) - total_slope + sum(
                (coefficients.get(d, Fraction(0)) for d in divisors(n)), Fraction(0)),
                f'fractional-part difference fails at {n}')
            if n > 1:
                discrepancy = coefficients.get(n, Fraction(0)) + mobius[n]
                require(discrepancy == sum(mobius[n//d]*(error[d]-error[d-1]) for d in divisors(n)),
                        f'coefficient inversion fails at {n}')
                require(discrepancy**2 <= 4*partial_error_squared*sum(divisors(n))**2,
                        f'coefficient estimate fails at {n}')
                total_checks += 1
        discrepancy_sum = sum(abs(coefficients.get(n, Fraction(0)) + mobius[n])
                              for n in range(2, limit + 1))
        require(discrepancy_sum**2 <= 9 * partial_error_squared * limit**3,
                'aggregate coefficient estimate fails')
    print(f'Checked {total_checks} exact coefficient identities and estimates, plus the arithmetic constants.')


if __name__ == '__main__':
    main()
