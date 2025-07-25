import streamlit as st
import json
from pathlib import Path

# Path to the JSON file
JSON_PATH = Path(__file__).parent / "inference_results.json"

# Load data from JSON using new caching decorator
@st.cache_data
def load_data():
    if not JSON_PATH.exists():
        st.error(f"File not found: {JSON_PATH}")
        return []
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# Write updated data back to JSON
def save_data(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Main App
def main():
    st.title("Inference Results QC & Re-correction")
    data = load_data()
    if not data:
        return

    # Select record index
    idx = st.number_input(
        "Select record index", min_value=0, max_value=len(data)-1, value=0, step=1
    )
    record = data[int(idx)]
    filename = record.get("filename")
    # Extract detected_plate from results if available
    # Extract detected_plate from both record and results if available
    # Trong result > results > plate
    main_record = record.get("result", record)

    # Lấy list kết quả
    results_list = main_record.get("results", [])

    # Khởi tạo giá trị mặc định
    detected_plate = ""

    # Nếu có ít nhất 1 kết quả thì lấy plate của phần tử đầu
    if results_list:
        detected_plate = results_list[0].get("plate", "")
    col1, col2 = st.columns(2)
    with col1:
        st.image(f"http://localhost:8002/{filename}", caption=filename)
    with col2:
        st.subheader("License Plate")
        # Use a form to update on submit/enter
        with st.form(key=f"form_{idx}"):
            new_plate = st.text_input("Detected Plate:", value=detected_plate)
            submitted = st.form_submit_button("Update")
            if submitted:
                # Update the plate in the nested results field
                if record.get("results") and len(record["results"]) > 0:
                    data[int(idx)]["results"][0]["plate"] = new_plate
                    save_data(data)
                    st.success("Plate updated in inference_results.json!")
                else:
                    st.error("No results field found for this record.")

if __name__ == "__main__":
    main()
