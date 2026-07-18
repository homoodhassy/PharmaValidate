"""
PharmaValidate - Precision Calculation Engine
Two-sample t-test assuming equal variance (pooled variance).
"""

import math
from statistics import mean, stdev


class PrecisionCalculator:
    """Statistical engine for precision validation."""

    DEFAULT_ALPHA = 0.05

    @staticmethod
    def _regularized_incomplete_beta(a, b, x):
        if hasattr(math, "betainc"):
            return math.betainc(a, b, x)
        # Continued-fraction approximation (Numerical Recipes)
        if x <= 0:
            return 0.0
        if x >= 1:
            return 1.0

        ln_beta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
        front = math.exp(a * math.log(x) + b * math.log(1.0 - x) - ln_beta) / a

        f = 1.0
        c = 1.0
        d = 1.0 - (a + b) * x / (a + 1.0)
        if abs(d) < 1e-30:
            d = 1e-30
        d = 1.0 / d
        result = d
        for m in range(1, 201):
            m2 = 2 * m
            aa = m * (b - m) * x / ((a + m2 - 1) * (a + m2))
            d = 1.0 + aa * d
            if abs(d) < 1e-30:
                d = 1e-30
            c = 1.0 + aa / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1.0 / d
            result *= d * c
            aa = -(a + m) * (a + b + m) * x / ((a + m2) * (a + m2 + 1))
            d = 1.0 + aa * d
            if abs(d) < 1e-30:
                d = 1e-30
            c = 1.0 + aa / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1.0 / d
            delta = d * c
            result *= delta
            if abs(delta - 1.0) < 1e-10:
                break
        return front * result

    @staticmethod
    def _student_t_cdf(t_value, df):
        """Student's t cumulative distribution function."""
        if df <= 0:
            return 0.5
        x = df / (df + t_value * t_value)
        ib = PrecisionCalculator._regularized_incomplete_beta(df / 2.0, 0.5, x)
        if t_value >= 0:
            return 1.0 - 0.5 * ib
        return 0.5 * ib

    @staticmethod
    def two_sample_ttest_equal_variance(sample_a, sample_b, alpha=DEFAULT_ALPHA):
        """
        Performs a two-sample t-test assuming equal variance (pooled SD).

        H0: the two population means are equal.
        PASS when p-value <= alpha (p must not exceed alpha).

        Returns dict with t_statistic, p_value, df, pooled_sd, alpha, status.
        """
        n1 = len(sample_a)
        n2 = len(sample_b)

        if n1 < 2 or n2 < 2:
            return {
                "t_statistic": None,
                "p_value": None,
                "df": None,
                "pooled_sd": None,
                "alpha": alpha,
                "status": "PENDING",
            }

        mean_a = mean(sample_a)
        mean_b = mean(sample_b)
        var_a = stdev(sample_a) ** 2
        var_b = stdev(sample_b) ** 2
        df = n1 + n2 - 2

        pooled_variance = ((n1 - 1) * var_a + (n2 - 1) * var_b) / df
        pooled_sd = math.sqrt(pooled_variance)

        if pooled_sd == 0:
            return {
                "t_statistic": 0.0,
                "p_value": 0.0,
                "df": df,
                "pooled_sd": 0.0,
                "alpha": alpha,
                "status": "PASS",
            }

        se = pooled_sd * math.sqrt(1.0 / n1 + 1.0 / n2)
        t_statistic = (mean_a - mean_b) / se

        cdf = PrecisionCalculator._student_t_cdf(abs(t_statistic), df)
        p_value = 2.0 * (1.0 - cdf)

        status = "PASS" if p_value <= alpha else "FAIL"

        return {
            "t_statistic": t_statistic,
            "p_value": p_value,
            "df": df,
            "pooled_sd": pooled_sd,
            "alpha": alpha,
            "status": status,
        }
