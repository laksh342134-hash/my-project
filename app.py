from pathlib import Path

import pandas as pd
from flask import Flask, render_template, request
from werkzeug.datastructures import FileStorage

from checker import check_duplicates, check_missing_values, detect_pii, risk_score


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
BASE_DIR = Path(__file__).parent
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}


def analyze_file(file_storage):
    filename = file_storage.filename or "uploaded file"
    extension = Path(filename).suffix.lower().lstrip(".")
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Upload a CSV, XLSX, or XLS file.")

    if extension == "csv":
        dataframe = pd.read_csv(file_storage)
    else:
        dataframe = pd.read_excel(file_storage)

    if dataframe.empty or len(dataframe.columns) == 0:
        raise ValueError("The uploaded file does not contain any data.")

    missing = check_missing_values(dataframe)
    pii_columns = detect_pii(dataframe)
    rows = []
    for column in dataframe.columns:
        missing_percent = float(missing[column])
        rows.append(
            {
                "name": str(column),
                "missing": missing_percent,
                "pii": pii_columns.get(column, "None"),
                "risk": risk_score(missing_percent, column in pii_columns),
            }
        )

    return {
        "filename": filename,
        "rows": rows,
        "row_count": len(dataframe),
        "column_count": len(dataframe.columns),
        "duplicate_count": int(check_duplicates(dataframe)),
        "pii_count": len(pii_columns),
        "high_risk_count": sum(row["risk"] == "High" for row in rows),
    }


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if not uploaded_file or not uploaded_file.filename:
            error = "Choose a data file before scanning."
        else:
            try:
                result = analyze_file(uploaded_file)
            except (ValueError, OSError, pd.errors.ParserError) as exc:
                error = str(exc)
            except Exception:
                error = "That file could not be read. Check its format and try again."
    return render_template("index.html", result=result, error=error)


@app.route("/demo", methods=["POST"])
def demo():
    try:
        with (BASE_DIR / "sample_data.csv").open("rb") as sample_file:
            result = analyze_file(
                FileStorage(stream=sample_file, filename="sample_data.csv")
            )
        result["filename"] = "sample_data.csv"
        return render_template("index.html", result=result)
    except Exception:
        return render_template(
            "index.html", error="The bundled sample file could not be read."
        )


if __name__ == "__main__":
    app.run(debug=True)
