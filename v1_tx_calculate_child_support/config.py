"""
config.py - Configuration values

Copyright (c) 2021 by Thomas J. Daley, J.D. All Rights Reserved.
"""
MONTHLY_NET_RESOURCES_CAP = 9200.0
US_IRC_PERSONAL_EXEMPTION = 0.0
US_IRC_STANDARD_DEDUCTION = 12400
US_MAX_SOC_SEC_WAGES = 137700
US_MEDICARE_RATE_1099 = .029
US_MEDICARE_RATE_W2 = .0145
US_SELF_EMPLOYMENT_FACTOR = .9235
US_SOC_SEC_RATE_1099 = .124
US_SOC_SEC_RATE_W2 = .062

"""
Row Index = Number of children before the court
Col Index = Number of children not before the court
"""
CHILD_SUPPORT_FACTORS = [
    [],
    [.2, .175, .16, .1475, .1360, .1333, .1314, .13],
    [.25, .225, .2063, .19, .1833, .1786, .175, .1722],
    [.3, .2738, .2520, .24, .2314, .225, .22, .216],
    [.35, .322, .3033, .29, .28, .2722, .266, .2609],
    [.4, .3733, .3543, .34, .3289, .32, .3127, .3067],
    [.4, .3771, .36, .3467, .336, .3273, .32, .3138],
    [.4, .38, .3644, .352, .3418, .3333, .3262, .32]
]
