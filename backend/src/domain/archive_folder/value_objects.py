from enum import StrEnum


class RetentionPeriod(StrEnum):
    """Saqlash muddati — archival retention period.

    Stored as the string value; Uzbek labels live in the frontend labels map.
    """

    YEARS_3 = "3_years"
    YEARS_5 = "5_years"
    YEARS_10 = "10_years"
    YEARS_25 = "25_years"
    YEARS_50 = "50_years"
    YEARS_75 = "75_years"
    PERMANENT = "permanent"
    EPK = "epk"
