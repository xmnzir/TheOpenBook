def explain(row):
    if row["variance"] > 0:
        return f"{row['type']} exceeded budget driven by higher activity."
    return f"{row['type']} remained below budget indicating efficiency or timing."
