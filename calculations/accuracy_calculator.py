"""
PharmaValidate v0.5
Accuracy Calculation Engine

This module contains ONLY mathematical calculations.

No UI.
No database.
No file handling.

Every Accuracy screen should call these functions.
"""

from statistics import mean, stdev
from math import sqrt


class AccuracyCalculator:
    """Mathematical engine for Accuracy validation."""

    # ---------------------------------------------------------
    # SST
    # ---------------------------------------------------------

    @staticmethod
    def sst_mean(responses):
        """
        Calculate average SST response.
        """
        if len(responses) == 0:
            return 0.0

        return mean(responses)

    @staticmethod
    def sst_sd(responses):
        """
        Sample Standard Deviation.
        """
        if len(responses) < 2:
            return 0.0

        return stdev(responses)

    @staticmethod
    def sst_rsd(responses):
        """
        %RSD of SST responses.
        """

        avg = AccuracyCalculator.sst_mean(responses)

        if avg == 0:
            return 0.0

        sd = AccuracyCalculator.sst_sd(responses)

        return (sd / avg) * 100

    # ---------------------------------------------------------
    # Matrix
    # ---------------------------------------------------------

    @staticmethod
    def matrix_response(matrix_values):
        """
        Average matrix response.
        """

        if len(matrix_values) == 0:
            return 0.0

        return mean(matrix_values)

    # ---------------------------------------------------------
    # Recovery Response
    # ---------------------------------------------------------

    @staticmethod
    def recovered_response(spike_response, matrix_response):
        """
        Recovered response.

        AT = Spike - Matrix
        """

        return spike_response - matrix_response

    # ---------------------------------------------------------
    # Recovery (mg)
    # ---------------------------------------------------------

    @staticmethod
    def recovery_mg(
        recovered_response,
        standard_weight,
        mean_sst_area,
        dilution_factor=1,
    ):
        """
        Recovery (mg)

        Recovery =
        (Recovered Response × Standard Weight × DF)
        /
        Mean SST Area
        """

        if mean_sst_area == 0:
            return 0.0

        return (
            recovered_response
            * standard_weight
            * dilution_factor
        ) / mean_sst_area

    # ---------------------------------------------------------
    # Percent Recovery
    # ---------------------------------------------------------

    @staticmethod
    def percent_recovery(
        recovered_mg,
        amount_added,
    ):
        """
        %Recovery
        """

        if amount_added == 0:
            return 0.0

        return (
            recovered_mg
            / amount_added
        ) * 100

    # ---------------------------------------------------------
    # Bias
    # ---------------------------------------------------------

    @staticmethod
    def percent_bias(recovery_percent):
        """
        Bias against 100%.
        """

        return recovery_percent - 100

    # ---------------------------------------------------------
    # Summary Statistics
    # ---------------------------------------------------------

    @staticmethod
    def average(values):

        if len(values) == 0:
            return 0.0

        return mean(values)

    @staticmethod
    def standard_deviation(values):

        if len(values) < 2:
            return 0.0

        return stdev(values)

    @staticmethod
    def rsd(values):

        avg = AccuracyCalculator.average(values)

        if avg == 0:
            return 0.0

        return (
            AccuracyCalculator.standard_deviation(values)
            / avg
        ) * 100

    # ---------------------------------------------------------
    # Degrees of Freedom
    # ---------------------------------------------------------

    @staticmethod
    def degrees_of_freedom(number_of_replicates):
        """
        DF = n - 1
        """

        if number_of_replicates <= 1:
            return 0

        return number_of_replicates - 1

    # ---------------------------------------------------------
    # Pooled Standard Deviation
    # ---------------------------------------------------------

    @staticmethod
    def pooled_standard_deviation(groups):
        """
        groups = [
            [80% recoveries],
            [100% recoveries],
            [120% recoveries]
        ]
        """

        numerator = 0
        denominator = 0

        for group in groups:

            if len(group) < 2:
                continue

            sd = stdev(group)
            df = len(group) - 1

            numerator += (df * (sd ** 2))
            denominator += df

        if denominator == 0:
            return 0.0

        return sqrt(numerator / denominator)