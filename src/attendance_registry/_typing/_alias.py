from datetime import (
    date,
    datetime,
)

DatetimeOrString = str | date | datetime
DateOrDateRange = DatetimeOrString | tuple[DatetimeOrString]
