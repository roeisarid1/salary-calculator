import pandas as pd

def calc_salary(df: pd.DataFrame, hourly_rate: float) -> dict:
    report_type_counts = df["סוג דיווח"].value_counts()
    vacation_days_count = int(report_type_counts.get("חופשה", 0))

    worked_days_df = df[df["סוג דיווח"] != "חופשה"].copy()
    travel_refund_total = int(worked_days_df.shape[0] * 26)

    worked_days_df["יציאה.1"] = pd.to_datetime(
        worked_days_df["יציאה.1"], format="%H:%M:%S", errors="coerce"
    )
    worked_days_df["סה''כ.1"] = pd.to_datetime(
        worked_days_df["סה''כ.1"], format="%H:%M:%S", errors="coerce"
    )

    if "יום" in worked_days_df.columns:
        worked_days_df["תאריך"] = pd.to_datetime(
            worked_days_df["יום"].str.extract(r"(\d{2}/\d{2})")[0],
            format="%d/%m",
            errors="coerce",
        )
        worked_days_df["תאריך"] = worked_days_df["תאריך"].apply(
            lambda d: d.replace(year=pd.Timestamp.today().year) if pd.notna(d) else pd.NaT
        )
    else:
        worked_days_df["תאריך"] = pd.Timestamp.today().normalize()

    worked_days_df["זמן יציאה"] = worked_days_df.apply(
        lambda r: pd.Timestamp.combine(r["תאריך"].date(), r["יציאה.1"].time())
        if pd.notna(r["יציאה.1"]) and pd.notna(r["תאריך"]) else pd.NaT,
        axis=1
    )

    def classify_shift(exit_dt):
        if pd.isna(exit_dt):
            return "רגילה"
        weekday = exit_dt.dayofweek
        hour = exit_dt.hour + exit_dt.minute / 60
        if 5 <= hour < 9:
            return "לילה"
        if (weekday == 4 and hour >= 16) or (weekday == 5):
            return "לילה"
        return "רגילה"

    worked_days_df["סוג משמרת"] = worked_days_df["זמן יציאה"].apply(classify_shift)

    worked_days_df["סה״כ שעות"] = (
        worked_days_df["סה''כ.1"].dt.hour.fillna(0)
        + worked_days_df["סה''כ.1"].dt.minute.fillna(0) / 60
        + worked_days_df["סה''כ.1"].dt.second.fillna(0) / 3600
    )

    totals = worked_days_df.groupby("סוג משמרת", dropna=False)["סה״כ שעות"].sum()
    night_hours = float(totals.get("לילה", 0.0))
    regular_hours = float(totals.get("רגילה", 0.0))

    total_salary = (
        hourly_rate * regular_hours
        + hourly_rate * 1.5 * night_hours
        + hourly_rate * 8 * vacation_days_count
        + travel_refund_total
    )

    return {
        "total_salary": round(float(total_salary), 2),
        "regular_hours": round(float(regular_hours), 2),
        "night_hours": round(float(night_hours), 2),
        "vacation_days": int(vacation_days_count),
        "travel_refund_total": int(travel_refund_total),
    }
