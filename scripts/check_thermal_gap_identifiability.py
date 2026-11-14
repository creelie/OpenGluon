"""Exact moments of two indistinguishable finite-sample spectral measures."""

from fractions import Fraction as F
from math import comb, prod


def family(samples):
    """Return rational moments and the gapped part of the matching measure."""
    nodes = tuple(F(i + 1, 2 * (samples + 2)) for i in range(samples + 1))
    moments = tuple(
        sum(F((-1)**j * comb(k, j) * 2, 2**(2 * (j + 1)))
            / (1 - F(1, 2**(j + 1))) for j in range(k + 1))
        for k in range(samples + 1)
    )
    corrections = []
    majorants = []
    for i, node in enumerate(nodes):
        others = tuple(other for j, other in enumerate(nodes) if i != j)
        denominator = prod(node - other for other in others)
        coefficients = [F(1)]
        for other in others:
            updated = [F(0)] * (len(coefficients) + 1)
            for k, value in enumerate(coefficients):
                updated[k] -= value * other
                updated[k + 1] += value
            coefficients = updated
        corrections.append(sum(value * moment for value, moment in zip(coefficients, moments)) / denominator)
        majorants.append(1 / abs(denominator))

    base = F(1, samples + 1)
    epsilon = base / (2 * max(majorants))
    weights = tuple(base - epsilon * correction for correction in corrections)
    return nodes, base, weights, epsilon, moments


def verify():
    verification_count = 0
    for samples in range(1, 13):
        nodes, base, weights, epsilon, moments = family(samples)
        if not all(F(0) < node < F(1, 2) for node in nodes):
            raise AssertionError('Gapped nodes are outside the required interval')
        if epsilon <= 0 or not all(weight >= base / 2 for weight in weights):
            raise AssertionError('Invalid positive spectral measure')
        for k, moment in enumerate(moments):
            gapped = sum(base * node**k for node in nodes)
            gapless = sum(weight * node**k for node, weight in zip(nodes, weights)) + epsilon * moment
            if gapped != gapless:
                raise AssertionError(f'Finite time sample {k} did not match')
            verification_count += 1
        if sum(weights) + epsilon != 1:
            raise AssertionError('Measure has the wrong total mass')
    print(f'Checked {verification_count} exact moment matches for 12 sample counts.')


if __name__ == '__main__':
    verify()
