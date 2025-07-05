import streamlit as st
import requests
import io
from docx import Document
from fpdf import FPDF

st.title("FormaIA - Générateur de Contenu de Formation IA")

# User input
with st.form("course_form"):
    topic = st.text_input("Sujet du cours", "Les bases du réseau informatique")
    level = st.selectbox("Niveau", ["débutant", "intermédiaire", "avancé"])
    submitted = st.form_submit_button("Générer le cours")

if submitted:
    with st.spinner("Génération en cours..."):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/generate-course",
                json={"topic": topic, "level": level}
            )
            response.raise_for_status()
            data = response.json()
            st.session_state["course_data"] = data
            st.success("Cours généré !")
        except Exception as e:
            st.error(f"Erreur lors de la génération : {e}")

# Display and export if course data exists
if "course_data" in st.session_state:
    data = st.session_state["course_data"]
    st.subheader(data["title"])
    st.markdown(f"**Plan :**\n{data['outline']}")
    st.markdown(f"**Résumé :**\n{data['summary']}")
    st.markdown(f"**Contenu brut :**\n{data['raw_content']}")

    export_col1, export_col2 = st.columns(2)
    with export_col1:
        if st.button("Exporter en Word (.docx)"):
            doc = Document()
            doc.add_heading(data["title"], 0)
            doc.add_heading("Plan", level=1)
            doc.add_paragraph(data["outline"])
            doc.add_heading("Résumé", level=1)
            doc.add_paragraph(data["summary"])
            doc.add_heading("Contenu brut", level=1)
            doc.add_paragraph(data["raw_content"])
            buf = io.BytesIO()
            doc.save(buf)
            buf.seek(0)
            st.download_button(
                label="Télécharger le Word",
                data=buf,
                file_name="cours_formaia.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    with export_col2:
        if st.button("Exporter en PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
            pdf.set_font("DejaVu", size=16)
            pdf.cell(0, 10, data["title"], ln=True, align="C")
            pdf.set_font("DejaVu", size=12)
            pdf.cell(0, 10, "Plan:", ln=True)
            pdf.multi_cell(0, 10, data["outline"])
            pdf.cell(0, 10, "Résumé:", ln=True)
            pdf.multi_cell(0, 10, data["summary"])
            pdf.cell(0, 10, "Contenu brut:", ln=True)
            pdf.multi_cell(0, 10, data["raw_content"])
            pdf_output = pdf.output(dest='S').encode('utf-8')
            st.download_button(
                label="Télécharger le PDF",
                data=pdf_output,
                file_name="cours_formaia.pdf",
                mime="application/pdf"
            )
