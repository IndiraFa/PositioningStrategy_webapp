import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import re
import scipy
# from pathlib import Path
from scipy.stats import shapiro
from scipy.stats import kstest
from scipy.stats import anderson
from calcul_nutriscore import plot
# from preprocess import Preprocessing

#path_with_outliers = 'src/datasets/nutrition_table_nutriscore_with_outliers.csv'
#data_with_outliers = pd.read_csv(path_with_outliers, sep=',')

path_no_outliers = 'src/datasets/nutrition_table_nutriscore_no_outliers.csv'
data_no_outliers = pd.read_csv(path_no_outliers, sep=',')


def nutriscore_analysis(data):
    nutriscore_mean = data['nutriscore'].mean()
    nutriscore_median = data['nutriscore'].median()
    nutriscore_max = data['nutriscore'].max()
    nutriscore_min = data['nutriscore'].min()
    return nutriscore_mean, nutriscore_median, nutriscore_max, nutriscore_min


# Shapiro test, for N>5000, computed p-value may not be accurate
def shapiro_test(data, column):
    x = data[column]
    shapiro_test_value = shapiro(
        x, axis=None, nan_policy='raise', keepdims=False
    )
    return shapiro_test_value


# Kolmogorov-Smirnov test
def ks_test(data, column):
    x = data[column]
    ks_test_value = kstest(x, 'norm', args=(x.mean(), x.std()))
    return ks_test_value


# Test de normalité d'Anderson-Darling
def ad_test(data, column):
    x = data[column]
    ad_test_value = anderson(x, 'norm')
    return ad_test_value


def skewness(data, column):
    x = data[column]
    skew_value = scipy.stats.skew(x, axis=0, bias=True)
    return skew_value


def kurtosis(data, column):
    x = data[column]
    kurtosis_value = scipy.stats.kurtosis(x, axis=0, fisher=False, bias=True)
    return kurtosis_value


def label_percentage(data, label):
    label_percent = data[data['label'] == label].shape[0]/data.shape[0]
    return label_percent


# with outliers
plot(
    data_with_outliers['nutriscore'],
    title='Nutriscore distribution with outliers',
    xlabel='Nutriscore',
    ylabel='Number of recipes',
    output_path='NS_with_outliers.png'
).plot_distrubution()
nutriscore_with_outliers_mean, nutriscore_with_outliers_median, \
    nutriscore_with_outliers_max, nutriscore_with_outliers_min = \
    nutriscore_analysis(data_with_outliers)

print(
    f"The mean value of the Nutri-Score with outliers is "
    f"{nutriscore_with_outliers_mean:.2f}"
)
print(
    f"The median value of the Nutri-Score with outliers is "
    f"{nutriscore_with_outliers_median:.2f}"
)
print(
    f"The maximum value of the Nutri-Score with outliers is "
    f"{nutriscore_with_outliers_max:.2f}"
)
print(
    f"The minimum value of the Nutri-Score with outliers is "
    f"{nutriscore_with_outliers_min:.2f}"
)

shapiro_test_with_outliers = shapiro_test(data_with_outliers, 'nutriscore')
print(shapiro_test_with_outliers)

ks_test_with_outliers = ks_test(data_with_outliers, 'nutriscore')
print(ks_test_with_outliers)

ad_test_with_outliers = ad_test(data_with_outliers, 'nutriscore')
print(ad_test_with_outliers)

skewness_with_outliers = skewness(data_with_outliers, 'nutriscore')
print(f"The Nutriscore skewness with outliers is {skewness_with_outliers}")

kurtosis_with_outliers = kurtosis(data_with_outliers, 'nutriscore')
print(f"The Nutriscore kurtosis with outliers is {kurtosis_with_outliers}")

plot(
    data_with_outliers['label'],
    title='Nutriscore label distribution with outliers',
    xlabel='Nutriscore label',
    ylabel='Number of recipes',
    output_path='NS_label_with_outliers.png'
).plot_distribution_label(labels=['A', 'B', 'C', 'D', 'E'])

for label in ['A', 'B', 'C', 'D', 'E']:
    label_percent = label_percentage(data_with_outliers, label)
    print(
        f"The percentage of recipes with Nutriscore {label} with outliers is "
        f"{label_percent * 100:.2f}%"
    )

# -----------------------------------
# without outliers

# plot NS, values
plot(
    data_no_outliers['nutriscore'],
    title='Nutriscore distribution no outliers',
    xlabel='Nutriscore', ylabel='Number of recipes',
    output_path='NS_no_outliers.png'
).plot_distrubution()
nutriscore_no_outliers_mean, nutriscore_no_outliers_median, \
    nutriscore_no_outliers_max, nutriscore_no_outliers_min =\
    nutriscore_analysis(data_no_outliers)

print(
    f"The mean value of the Nutri-Score without outliers is "
    f"{nutriscore_no_outliers_mean:.2f}"
)
print(
    f"The median value of the Nutri-Score without outliers is "
    f"{nutriscore_no_outliers_median:.2f}"
)
print(
    f"The maximum value of the Nutri-Score without outliers is "
    f"{nutriscore_no_outliers_max:.2f}"
)
print(
    f"The minimum value of the Nutri-Score without outliers is "
    f"{nutriscore_no_outliers_min:.2f}"
)

# Shapiro test, for N>5000, computed p-value may not be accurate
shapiro_test_no_outliers = shapiro_test(data_no_outliers, 'nutriscore')
print(shapiro_test_no_outliers)

# Kolmogorov-Smirnov test
ks_test_no_outliers = ks_test(data_no_outliers, 'nutriscore')
print(ks_test_no_outliers)

# Test de normalité d'Anderson-Darling
ad_test_no_outliers = ad_test(data_no_outliers, 'nutriscore')
print(ad_test_no_outliers)

# skewness
skewness_no_outliers = skewness(data_no_outliers, 'nutriscore')
print(f"The Nutriscore skewness without outliers is {skewness_no_outliers}")

# kurtosis
kurtosis_no_outliers = kurtosis(data_no_outliers, 'nutriscore')
print(f"The Nutriscore kurtosis without outliers is {kurtosis_no_outliers}")


# plot NS, labels
plot(
    data_no_outliers['label'],
    title='Nutriscore label distribution no outliers',
    xlabel='Nutriscore label',
    ylabel='Number of recipes',
    output_path='NS_label_no_outliers.png'
).plot_distribution_label(labels=['A', 'B', 'C', 'D', 'E'])

for label in ['A', 'B', 'C', 'D', 'E']:
    label_percent = label_percentage(data_no_outliers, label)
    print(
        f"The percentage of recipes with Nutriscore {label} without outliers "
        f"is {label_percent * 100:.2f}%"
    )
