# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 10:53:43 2025

@author: A397778
"""
import streamlit as st
import json
import pandas as pd
import os
from io import BytesIO

def relabel_type(value):
    type_mapping = {
        "text": "Free Text",
        "boolean": "Yes/No",
        "datetime": "Date+time",
        "phone_number": "Phone No.",
        "group": "Sub Form"
    }
    return type_mapping.get(value, value.capitalize())

def flatten_json(children, parent_title=None):
    rows = []
    for item in children:
        row = {"Parent Title": "" if parent_title == data.get("title", "Unknown") else parent_title}
        
        options = item.get("options", [])
        row["Options Texts"] = ", ".join(opt.get("text", "") for opt in options)
        row["Options Identifiers"] = ", ".join(opt.get("identifier", "") for opt in options if "identifier" in opt)
        
        row.update({
            k: (
                "Yes" if v is True else 
                relabel_type(v) if k == "type" else 
                ("Yes" if k in ["required_rule", "readonly_rule"] and v == "always" else None) if k in ["required_rule", "readonly_rule"] else v
            )
            for k, v in item.items() if k != "children" and k != "options"
        })
        
        for key in ["required_rule", "readonly_rule"]:
            if key in row and row[key] is None:
                row.pop(key)
        
        rows.append(row)
        
        if "children" in item:
            rows.extend(flatten_json(item["children"], parent_title=item.get("title", "Unknown")))
    return rows

def convert_json_to_xlsx(json_data):
    global data
    data = json_data
    rows = flatten_json(data.get("children", []), parent_title=data.get("title", "Unknown"))
    df = pd.DataFrame(rows)
    
    column_order = [
        "title", "identifier", "type", "Options Texts", "Options Identifiers", "Parent Title", 
        "required_rule", "readonly_rule", "multi_line", "multiple" , "timestamp", "geostamp", "hidden", 
        "hint", "required_expr", "validate_expr", "calculate_expr", "type_derived", "initialAnswer"
    ]
    
    empty_df = pd.DataFrame(columns=column_order)
    df = pd.concat([empty_df, df], ignore_index=True)
    df = df.reindex(columns=column_order)
    
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output

st.title("JSON to Excel Converter")

uploaded_file = st.file_uploader("Upload JSON File", type="json")

if uploaded_file:
    json_data = json.load(uploaded_file)
    st.success("File uploaded successfully!")
    
    if st.button("Convert to Excel"):
        excel_file = convert_json_to_xlsx(json_data)
        st.session_state["excel_file"] = excel_file
        st.success("Conversion successful! You can now download the file.")
        
    if "excel_file" in st.session_state:
        st.download_button(
            label="Download Excel File",
            data=st.session_state["excel_file"],
            file_name="converted_file.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )