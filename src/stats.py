"""
Objects and methods for collecting data statistics.
"""


from typing import Tuple
from scipy import stats
import numpy as np
from src.plot import MetricData


def _reduction(data: np.ndarray, baseline: np.ndarray) -> float:
    """
    Returns the percent the baseline mean was reduced by
    according to the mean data.

    For example: If the mean of the baseline is 10 and
    the mean of the data is 8, 0.2 will be returned.

    @param data: The reduced data
    @param baseline: The baseline data
    @returns the percent the baseline was reduced by.
    """
    data_mean = np.mean(data)
    baseline_mean = np.mean(baseline)
    r = (baseline_mean - data_mean) / baseline_mean
    return float(r)


class MetricStats:
    """
    Calculates summary statistics for a MetricData object.
    """
    def __init__(self, data: MetricData):
        """
        @param data: The MetricData object to evaluate
        """
        self.data = data

    def test_chainguard_lt_rapidfort(self) -> Tuple[float, float]:
        """
        Returns a one-tailed paired t test on Chainguard vs RapidFort.
        The null hypothesis is that the means of both vendors is
        the same. The alternative hypothesis is the mean of the
        Chainguard data is less than the RapidFort data mean.

        This method uses scikit.ttest_rel().

        @returns a Tuple of the t statistic and p value (t_stat, p_val)
        """
        t_stat, p_val = stats.ttest_rel(self.data.chainguard,
                                        self.data.rapidfort,
                                        alternative="less")
        return float(t_stat), float(p_val)

    def test_rapidfort_lt_chainguard(self) -> Tuple[float, float]:
        """
        Returns a one-tailed paired t test on Chainguard vs RapidFort.
        The null hypothesis is that the means of both vendors is
        the same. The alternative hypothesis is the mean of the
        RapidFort data is less than the Cahinguard data mean.

        This method uses scikit.ttest_rel().

        @returns a Tuple of the t statistic and p value (t_stat, p_val)
        """
        t_stat, p_val = stats.ttest_rel(self.data.rapidfort,
                                        self.data.chainguard,
                                        alternative="less")
        return float(t_stat), float(p_val)

    def chainguard_reduction(self) -> float:
        """
        Returns the difference between the Chainguard data mean and
        Baseline data mean as a percent of the Baseline data mean.

        @returns percent difference
        """
        return _reduction(self.data.chainguard, self.data.baseline)

    def rapidfort_reduction(self) -> float:
        """
        Returns the difference between the RapidFort data mean and
        Baseline data mean as a percent of the Baseline data mean.

        @returns percent difference
        """
        return _reduction(self.data.rapidfort, self.data.baseline)
