"""Replay the rational constants in the conditional one-scale Yang-Mills note."""

from fractions import Fraction


def main():
    mesh_ratio = 20
    cut_factor = 1 / (1 - Fraction(12, mesh_ratio))
    seed_factor = (4 * mesh_ratio) ** 3 * cut_factor
    recurrence_factor = 8 * cut_factor
    assert cut_factor == Fraction(5, 2)
    assert seed_factor == 1_280_000
    assert recurrence_factor == 20

    original_seed = Fraction(1, 35_389_440)
    rows = [
        (Fraction(1, 32_000_000), Fraction(1, 25), Fraction(49, 48),
         Fraction(2401, 2880), Fraction(1324, 12500)),
        (Fraction(3, 81_920_000), Fraction(3, 64), Fraction(41, 40),
         Fraction(5043, 5120), Fraction(37, 125)),
        (Fraction(1, 26_880_000), Fraction(1, 21), Fraction(127, 124),
         Fraction(80645, 80724), Fraction(277, 875)),
    ]

    for seed, interval, majorant, expected_contraction, improvement in rows:
        assert seed_factor * seed == interval
        assert 0 < interval < 3
        # The power-series proof bounds (exp(y)-1)/y by this increasing function.
        exponential_bound = 1 + interval / (2 * (1 - interval / 3))
        assert exponential_bound <= majorant
        quadratic_factor = recurrence_factor * majorant ** 2
        contraction = quadratic_factor * interval
        assert contraction == expected_contraction
        assert 0 < contraction < 1
        assert majorant / quadratic_factor < 1
        assert seed / original_seed - 1 == improvement

    print('Checked all three conditional seed bounds and exact contraction constants.')


if __name__ == '__main__':
    main()
