import io
import pandas as pd

df = pd.read_csv("dataset.csv", encoding="utf-8")

CATEGORICAL_COLS = ["member_casual", "ended_at"]
NUMERIC_COLS = [c for c in df.columns if c not in CATEGORICAL_COLS]


def _report_lines():
    lines = [str(df.shape)]

    buf = io.StringIO()
    df.info(buf=buf)
    lines.append(buf.getvalue())

    lines.append("Пропуски по колонкам:")
    lines.append(df.isna().sum().to_string())
    lines.append("")

    lines.append("Колонка> среднее; медиана; отклонение")
    for col in NUMERIC_COLS:
        if pd.api.types.is_numeric_dtype(df[col]):
            lines.append(
                f"{col}> {df[col].mean():.2f}; {df[col].median():.2f}; {df[col].std():.2f}"
            )
    lines.append("")

    for col in CATEGORICAL_COLS:
        if col in df.columns:
            lines.append(f"--- {col} ---")
            lines.append(df[col].value_counts().to_string())
            lines.append("")

    return lines


if __name__ == "__main__":
    text = "\n".join(_report_lines())
    print(text)
    with open("report.txt", "w", encoding="utf-8") as f:
        f.write(text)