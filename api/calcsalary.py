import pandas as pd
from typing import Dict, Tuple

class SalaryConstants:
    TRAVEL_REFUND_PER_DAY = 26
    NIGHT_SHIFT_MULTIPLIER = 1.5
    VACATION_HOURS_PER_DAY = 8
    
    NIGHT_SHIFT_START_HOUR = 5
    NIGHT_SHIFT_END_HOUR = 9
    FRIDAY_NIGHT_START_HOUR = 16
    
    FRIDAY = 4
    SATURDAY = 5

class ColumnNames:
    REPORT_TYPE = "סוג דיווח"
    EXIT_TIME = "יציאה.1"
    TOTAL_HOURS = "סה''כ.1"
    DAY = "יום"
    VACATION = "חופשה"

def _parse_datetime_columns(timesheet_data: pd.DataFrame) -> pd.DataFrame:
    time_columns = [ColumnNames.EXIT_TIME, ColumnNames.TOTAL_HOURS]
    for col in time_columns:
        if col in timesheet_data.columns:
            timesheet_data[col] = pd.to_datetime(
                timesheet_data[col], 
                format="%H:%M:%S", 
                errors="coerce"
            )
    
    if ColumnNames.DAY in timesheet_data.columns:
        date_pattern = timesheet_data[ColumnNames.DAY].str.extract(r"(\d{2}/\d{2})")[0]
        parsed_dates = pd.to_datetime(date_pattern, format="%d/%m", errors="coerce")
        
        current_year = pd.Timestamp.today().year
        timesheet_data["parsed_date"] = parsed_dates.apply(
            lambda d: d.replace(year=current_year) if pd.notna(d) else pd.NaT
        )
    else:
        timesheet_data["parsed_date"] = pd.Timestamp.today().normalize()
    
    return timesheet_data

def _create_exit_datetime(timesheet_data: pd.DataFrame) -> pd.Series:
    def combine_datetime(row):
        if pd.notna(row[ColumnNames.EXIT_TIME]) and pd.notna(row["parsed_date"]):
            return pd.Timestamp.combine(
                row["parsed_date"].date(), 
                row[ColumnNames.EXIT_TIME].time()
            )
        return pd.NaT
    
    return timesheet_data.apply(combine_datetime, axis=1)

def _classify_shift_vectorized(exit_datetimes: pd.Series) -> pd.Series:
    shift_types = pd.Series("רגילה", index=exit_datetimes.index)
    
    valid_times = exit_datetimes.notna()
    
    hours = (
        exit_datetimes.dt.hour + 
        exit_datetimes.dt.minute / 60
    )
    
    weekdays = exit_datetimes.dt.dayofweek
    
    early_morning = (
        valid_times & 
        (hours >= SalaryConstants.NIGHT_SHIFT_START_HOUR) & 
        (hours < SalaryConstants.NIGHT_SHIFT_END_HOUR)
    )
    
    friday_evening = (
        valid_times & 
        (weekdays == SalaryConstants.FRIDAY) & 
        (hours >= SalaryConstants.FRIDAY_NIGHT_START_HOUR)
    )
    
    saturday_all_day = (
        valid_times & 
        (weekdays == SalaryConstants.SATURDAY)
    )
    
    night_shift_mask = early_morning | friday_evening | saturday_all_day
    shift_types[night_shift_mask] = "לילה"
    
    return shift_types

def _calculate_total_hours_vectorized(timesheet_data: pd.DataFrame) -> pd.Series:
    total_hours_col = timesheet_data[ColumnNames.TOTAL_HOURS]
    
    return (
        total_hours_col.dt.hour.fillna(0) +
        total_hours_col.dt.minute.fillna(0) / 60 +
        total_hours_col.dt.second.fillna(0) / 3600
    )

def calc_salary(timesheet_df: pd.DataFrame, hourly_rate: float) -> Dict[str, float]:
    report_type_counts = timesheet_df[ColumnNames.REPORT_TYPE].value_counts()
    vacation_days_count = int(report_type_counts.get(ColumnNames.VACATION, 0))
    
    work_days_data = timesheet_df[
        timesheet_df[ColumnNames.REPORT_TYPE] != ColumnNames.VACATION
    ].copy()
    
    travel_refund_total = len(work_days_data) * SalaryConstants.TRAVEL_REFUND_PER_DAY
    
    if work_days_data.empty:
        return {
            "total_salary": round(float(hourly_rate * SalaryConstants.VACATION_HOURS_PER_DAY * vacation_days_count + travel_refund_total), 2),
            "regular_hours": 0.0,
            "night_hours": 0.0,
            "vacation_days": vacation_days_count,
            "travel_refund_total": travel_refund_total,
        }
    
    work_days_data = _parse_datetime_columns(work_days_data)
    
    work_days_data["full_exit_datetime"] = _create_exit_datetime(work_days_data)
    
    work_days_data["shift_type"] = _classify_shift_vectorized(work_days_data["full_exit_datetime"])
    
    work_days_data["total_hours_decimal"] = _calculate_total_hours_vectorized(work_days_data)
    
    hours_by_shift = work_days_data.groupby("shift_type", dropna=False)["total_hours_decimal"].sum()
    
    night_hours = float(hours_by_shift.get("לילה", 0.0))
    regular_hours = float(hours_by_shift.get("רגילה", 0.0))
    
    total_salary = (
        hourly_rate * regular_hours +
        hourly_rate * SalaryConstants.NIGHT_SHIFT_MULTIPLIER * night_hours +
        hourly_rate * SalaryConstants.VACATION_HOURS_PER_DAY * vacation_days_count +
        travel_refund_total
    )
    
    return {
        "total_salary": round(float(total_salary), 2),
        "regular_hours": round(float(regular_hours), 2),
        "night_hours": round(float(night_hours), 2),
        "vacation_days": int(vacation_days_count),
        "travel_refund_total": int(travel_refund_total),
    }
