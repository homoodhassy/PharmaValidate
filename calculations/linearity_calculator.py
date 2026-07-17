"""
PharmaValidate v0.5 - Linearity Calculation Engine
This module contains mathematical functions for least-squares linear regression,
pooled % RSD, and percent y-intercept calculations.
"""

import math
from statistics import mean, stdev

class LinearityCalculator:
    """Mathematical engine for Linearity validation."""

    @staticmethod
    def linear_regression(x_values, y_values):
        """
        Performs least-squares linear regression on individual (x, y) data points.
        Returns:
            slope (m)
            intercept (c)
            r_square (R^2)
            multiple_r (r)
            rss (Residual Sum of Squares)
        """
        n = len(x_values)
        if n < 3:
            return 0.0, 0.0, 0.0, 0.0, 0.0

        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xx = sum(x ** 2 for x in x_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))

        # Slope m
        denom = (n * sum_xx - sum_x ** 2)
        if denom == 0:
            return 0.0, 0.0, 0.0, 0.0, 0.0
        m = (n * sum_xy - sum_x * sum_y) / denom

        # Intercept c
        c = (sum_y - m * sum_x) / n

        # Residual Sum of Squares (RSS)
        rss = sum((y - (m * x + c)) ** 2 for x, y in zip(x_values, y_values))

        # Total Sum of Squares (TSS)
        y_mean = sum_y / n
        tss = sum((y - y_mean) ** 2 for y in y_values)

        # R-Square (R^2)
        r_square = 1.0 - (rss / tss) if tss > 0 else 0.0
        
        # Multiple R (Correlation Coefficient, r)
        multiple_r = math.sqrt(max(0.0, r_square))

        return m, c, r_square, multiple_r, rss

    @staticmethod
    def calculate_percent_y_intercept(intercept, mean_response_100):
        """
        Calculates % y-intercept relative to the 100% nominal level response.
        Formula: (% y-intercept = |c| / Mean Response at 100% level * 100)
        """
        if mean_response_100 == 0:
            return 0.0
        return (abs(intercept) / mean_response_100) * 100

    @staticmethod
    def calculate_pooled_rsd(levels_data):
        """
        Calculates the pooled % RSD across multiple levels.
        levels_data: List of lists, where each sub-list contains the replicate responses for a level.
        Example: [[1001, 1005, 998], [1200, 1205, 1195], ...]
        """
        total_variance_terms = 0.0
        total_df = 0
        all_responses = []

        for reps in levels_data:
            if len(reps) < 2:
                continue
            sd_val = stdev(reps)
            df = len(reps) - 1
            total_variance_terms += df * (sd_val ** 2)
            total_df += df
            all_responses.extend(reps)

        if total_df == 0 or len(all_responses) == 0:
            return 0.0, 0.0

        pooled_sd = math.sqrt(total_variance_terms / total_df)
        grand_mean = mean(all_responses)
        pooled_rsd = (pooled_sd / grand_mean) * 100 if grand_mean > 0 else 0.0

        return pooled_sd, pooled_rsd