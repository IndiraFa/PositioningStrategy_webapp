import logging
import pandas as pd
import scipy
from scipy.stats import shapiro, kstest, anderson
from calcul_nutriscore import Plot

logger = logging.getLogger("nutriscore_analysis")


def nutriscore_analysis(data):
    """
    Analyze the Nutri-Score of the recipes.

    Parameters
    ----------
    data: pd.DataFrame
        DataFrame with the nutrition table and the Nutri-Score.

    Returns
    -------
    Tuple
        Tuple with the mean, median, max, and min values of the Nutri-Score.
    """
    try:
        nutriscore_mean = data['nutriscore'].mean()
        nutriscore_median = data['nutriscore'].median()
        nutriscore_max = data['nutriscore'].max()
        nutriscore_min = data['nutriscore'].min()
        logger.info("Nutri-Score analysis completed successfully.")
        return nutriscore_mean, nutriscore_median, nutriscore_max, \
            nutriscore_min
    except Exception as e:
        logger.error(f"Error in nutriscore_analysis: {e}")
        raise


def shapiro_test(data, column):
    """
    Test the normality of the data using the Shapiro-Wilk test.
    Parameters
    ----------
    data: pd.DataFrame
        DataFrame with the nutrition table and the Nutri-Score.
    column: str
        Column name with the Nutri-Score.

    Returns
    -------
    Tuple
        Tuple with the test statistic and the p-value.
    """
    try:
        x = data[column]
        shapiro_test_value = shapiro(
            x, axis=None, nan_policy='raise', keepdims=False
        )
        logger.info("Shapiro test completed successfully.")
        return shapiro_test_value
    except Exception as e:
        logger.error(f"Error in shapiro_test: {e}")
        raise


def ks_test(data, column):
    """
    Test the normality of the data using the Kolmogorov-Smirnov test.

    Parameters
    ----------
    data: pd.DataFrame
        DataFrame with the nutrition table and the Nutri-Score.
    column: str
        Column name with the Nutri-Score.

    Returns
    -------
    Tuple
        Tuple with the test statistic and the p-value.
    """
    try:
        x = data[column]
        ks_test_value = kstest(x, 'norm', args=(x.mean(), x.std()))
        logger.info("Kolmogorov-Smirnov test completed successfully.")
        return ks_test_value
    except Exception as e:
        logger.error(f"Error in ks_test: {e}")
        raise


def ad_test(data, column):
    """
    Test the normality of the data using the Anderson-Darling test.

    Parameters
    ----------
    data: pd.DataFrame
        DataFrame with the nutrition table and the Nutri-Score.
    column: str
        Column name with the Nutri-Score.

    Returns
    -------
    Tuple
        Tuple with the test statistic and the critical values.
    """
    try:
        x = data[column]
        ad_test_value = anderson(x, 'norm')
        logger.info("Anderson-Darling test completed successfully.")
        return ad_test_value
    except Exception as e:
        logger.error(f"Error in ad_test: {e}")
        raise


def skewness(data, column):
    """
    Calculate the skewness of the data.

    Parameters
    ----------
    data: pd.DataFrame
        DataFrame with the nutrition table and the Nutri-Score.
    column: str
        Column name with the Nutri-Score.

    Returns
    -------
    float
        Skewness value.
    """
    try:
        x = data[column]
        skew_value = scipy.stats.skew(x, axis=0, bias=True)
        logger.info("Skewness calculation completed successfully.")
        return skew_value
    except Exception as e:
        logger.error(f"Error in skewness: {e}")
        raise


def kurtosis(data, column):
    """
    Calculate the kurtosis of the data.

    Parameters
    ----------
    data: pd.DataFrame
        DataFrame with the nutrition table and the Nutri-Score.
    column: str
        Column name with the Nutri-Score.

    Returns
    -------
    float
        Kurtosis value.
    """
    try:
        x = data[column]
        kurtosis_value = scipy.stats.kurtosis(
            x, axis=0, fisher=False, bias=True
        )
        logger.info("Kurtosis calculation completed successfully.")
        return kurtosis_value
    except Exception as e:
        logger.error(f"Error in kurtosis: {e}")
        raise


def label_percentage(data, label):
    """
    Calculate the percentage of recipes with a specific Nutri-Score label.

    Parameters
    ----------
    data: pd.DataFrame
        DataFrame with the nutrition table and the Nutri-Score.
    label: str
        Label of the Nutri-Score.

    Returns
    -------
    label_percent: float
    """
    try:
        label_percent = data[data['label'] == label].shape[0] / data.shape[0]
        logger.info(f"Label percentage for {label} calculated successfully.")
        return label_percent
    except Exception as e:
        logger.error(f"Error in label_percentage: {e}")
        raise


def main():
    """
    Main function to analyze the Nutri-Score of the recipes.

    Returns
    -------
    None
    """
    try:
        path_with_outliers = (
            './datasets/nutrition_table_nutriscore_with_outliers.csv'
        )
        data_with_outliers = pd.read_csv(path_with_outliers, sep=',')
        logger.info("Data with outliers loaded successfully.")

        path_no_outliers = (
            './datasets/nutrition_table_nutriscore_no_outliers.csv'
        )
        data_no_outliers = pd.read_csv(path_no_outliers, sep=',')
        logger.info("Data without outliers loaded successfully.")

        Plot(
            data_with_outliers['nutriscore'],
            title='Nutriscore distribution with outliers',
            xlabel='Nutriscore',
            ylabel='Number of recipes',
            output_path='NS_with_outliers.png'
        ).plot_distribution()
        logger.info(
            "Plot for Nutriscore distribution with outliers created \
                successfully."
        )

        nutriscore_with_outliers_mean, nutriscore_with_outliers_median, \
            nutriscore_with_outliers_max, nutriscore_with_outliers_min = \
            nutriscore_analysis(data_with_outliers)

        logger.debug(
            f"The mean value of the Nutri-Score with outliers is "
            f"{nutriscore_with_outliers_mean:.2f}"
        )
        logger.debug(
            f"The median value of the Nutri-Score with outliers is "
            f"{nutriscore_with_outliers_median:.2f}"
        )
        logger.debug(
            f"The maximum value of the Nutri-Score with outliers is "
            f"{nutriscore_with_outliers_max:.2f}"
        )
        logger.debug(
            f"The minimum value of the Nutri-Score with outliers is "
            f"{nutriscore_with_outliers_min:.2f}"
        )

        shapiro_test_with_outliers = shapiro_test(
            data_with_outliers,
            'nutriscore'
        )
        logger.debug(shapiro_test_with_outliers)

        ks_test_with_outliers = ks_test(data_with_outliers, 'nutriscore')
        logger.debug(ks_test_with_outliers)

        ad_test_with_outliers = ad_test(data_with_outliers, 'nutriscore')
        logger.debug(ad_test_with_outliers)

        skewness_with_outliers = skewness(data_with_outliers, 'nutriscore')
        logger.debug(
            f"The Nutriscore skewness with outliers is \
                {skewness_with_outliers}"
        )

        kurtosis_with_outliers = kurtosis(data_with_outliers, 'nutriscore')
        logger.debug(
            f"The Nutriscore kurtosis with outliers is \
                {kurtosis_with_outliers}"
        )

        Plot(
            data_with_outliers['label'],
            title='Nutriscore label distribution with outliers',
            xlabel='Nutriscore label',
            ylabel='Number of recipes',
            output_path='NS_label_with_outliers.png'
        ).plot_distribution_label(labels=['A', 'B', 'C', 'D', 'E'])
        logger.info("Plot for Nutriscore label distribution with outliers \
                    created successfully.")

        for label in ['A', 'B', 'C', 'D', 'E']:
            label_percent = label_percentage(data_with_outliers, label)
            logger.debug(
                f"The percentage of recipes with Nutriscore {label} with \
                    outliers is "
                f"{label_percent * 100:.2f}%"
            )

        Plot(
            data_no_outliers['nutriscore'],
            title='Nutriscore distribution no outliers',
            xlabel='Nutriscore', ylabel='Number of recipes',
            output_path='NS_no_outliers.png'
        ).plot_distribution()
        logger.info("Plot for Nutriscore distribution without outliers \
                    created successfully.")

        nutriscore_no_outliers_mean, nutriscore_no_outliers_median, \
            nutriscore_no_outliers_max, nutriscore_no_outliers_min = \
            nutriscore_analysis(data_no_outliers)

        logger.debug(
            f"The mean value of the Nutri-Score without outliers is "
            f"{nutriscore_no_outliers_mean:.2f}"
        )
        logger.debug(
            f"The median value of the Nutri-Score without outliers is "
            f"{nutriscore_no_outliers_median:.2f}"
        )
        logger.debug(
            f"The maximum value of the Nutri-Score without outliers is "
            f"{nutriscore_no_outliers_max:.2f}"
        )
        logger.debug(
            f"The minimum value of the Nutri-Score without outliers is "
            f"{nutriscore_no_outliers_min:.2f}"
        )

        shapiro_test_no_outliers = shapiro_test(data_no_outliers, 'nutriscore')
        logger.debug(shapiro_test_no_outliers)

        ks_test_no_outliers = ks_test(data_no_outliers, 'nutriscore')
        logger.debug(ks_test_no_outliers)

        ad_test_no_outliers = ad_test(data_no_outliers, 'nutriscore')
        logger.debug(ad_test_no_outliers)

        skewness_no_outliers = skewness(data_no_outliers, 'nutriscore')
        logger.debug(f"The Nutriscore skewness without outliers is \
              {skewness_no_outliers}")

        kurtosis_no_outliers = kurtosis(data_no_outliers, 'nutriscore')
        logger.debug(f"The Nutriscore kurtosis without outliers is \
              {kurtosis_no_outliers}")

        Plot(
            data_no_outliers['label'],
            title='Nutriscore label distribution no outliers',
            xlabel='Nutriscore label',
            ylabel='Number of recipes',
            output_path='NS_label_no_outliers.png'
        ).plot_distribution_label(labels=['A', 'B', 'C', 'D', 'E'])
        logger.info("Plot for Nutriscore label distribution without outliers \
                    created successfully.")

        for label in ['A', 'B', 'C', 'D', 'E']:
            label_percent = label_percentage(data_no_outliers, label)
            logger.debug(
                f"The percentage of recipes with Nutriscore {label} without \
                    outliers "
                f"is {label_percent * 100:.2f}%"
            )
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()
