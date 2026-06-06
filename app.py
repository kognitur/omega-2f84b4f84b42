import streamlit as st
from PIL import Image
import pytesseract
import io
import os
import tempfile
from pdf2image import convert_from_bytes
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="PaperText OCR - Screenshot to Text Converter",
    page_icon="📄",
    layout="wide"
)

st.title("📄 PaperText OCR")
st.markdown("### Convert screenshots of papers and articles into clean, searchable text")
st.markdown("---")

# Initialize session state
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""
if 'filename' not in st.session_state:
    st.session_state.filename = ""

# File upload section
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Upload a screenshot or PDF",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'pdf'],
        help="Supported formats: PNG, JPG, JPEG, BMP, TIFF, PDF"
    )

with col2:
    st.markdown("### Settings")
    lang = st.selectbox(
        "Language",
        options=['eng', 'eng+fra', 'eng+deu', 'eng+spa', 'eng+ita'],
        format_func=lambda x: {'eng': 'English', 'eng+fra': 'English + French', 
                              'eng+deu': 'English + German', 'eng+spa': 'English + Spanish',
                              'eng+ita': 'English + Italian'}[x]
    )
    
    psm = st.selectbox(
        "Page Segmentation Mode",
        options=[3, 4, 6, 11, 12],
        format_func=lambda x: {
            3: "Automatic (default)",
            4: "Single column",
            6: "Uniform block",
            11: "Single text line",
            12: "Single word"
        }[x]
    )

# Process file
if uploaded_file is not None:
    try:
        with st.spinner("Processing your file..."):
            file_extension = uploaded_file.name.split('.')[-1].lower()
            st.session_state.filename = uploaded_file.name
            
            # Handle PDF files
            if file_extension == 'pdf':
                pdf_bytes = uploaded_file.read()
                images = convert_from_bytes(pdf_bytes, dpi=300)
                text_parts = []
                
                progress_bar = st.progress(0)
                for i, image in enumerate(images):
                    text = pytesseract.image_to_string(
                        image, 
                        lang=lang,
                        config=f'--psm {psm}'
                    )
                    text_parts.append(f"--- Page {i+1} ---\n{text}")
                    progress_bar.progress((i + 1) / len(images))
                
                st.session_state.extracted_text = "\n\n".join(text_parts)
                
            # Handle image files
            else:
                image = Image.open(uploaded_file)
                st.session_state.extracted_text = pytesseract.image_to_string(
                    image,
                    lang=lang,
                    config=f'--psm {psm}'
                )
            
            st.success("✅ Text extracted successfully!")
            
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.info("Please make sure the file is valid and try again.")

# Display results
if st.session_state.extracted_text:
    st.markdown("---")
    st.markdown("### Extracted Text")
    
    # Preview
    with st.expander("Preview", expanded=True):
        st.text_area(
            "Text output",
            value=st.session_state.extracted_text,
            height=300,
            disabled=True
        )
    
    # Download options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download as TXT
        txt_buffer = io.BytesIO()
        txt_buffer.write(st.session_state.extracted_text.encode('utf-8'))
        txt_buffer.seek(0)
        
        st.download_button(
            label="📥 Download as TXT",
            data=txt_buffer,
            file_name=f"{st.session_state.filename}_ocr.txt",
            mime="text/plain"
        )
    
    with col2:
        # Download as CSV
        csv_buffer = io.BytesIO()
        df = pd.DataFrame({
            'filename': [st.session_state.filename],
            'extracted_text': [st.session_state.extracted_text],
            'timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        st.download_button(
            label="📊 Download as CSV",
            data=csv_buffer,
            file_name=f"{st.session_state.filename}_ocr.csv",
            mime="text/csv"
        )
    
    with col3:
        # Copy to clipboard
        if st.button("📋 Copy to Clipboard"):
            st.write("Text copied! (Use Ctrl+C or Cmd+C)")
            st.session_state.clipboard_text = st.session_state.extracted_text

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>PaperText OCR v1.0 | Built for researchers</p>
        <p style='font-size: 0.8em;'>Supports: PNG, JPG, JPEG, BMP, TIFF, PDF</p>
    </div>
""", unsafe_allow_html=True)

# Requirements file
requirements_content = """
streamlit>=1.28.0
Pillow>=10.0.0
pytesseract>=0.3.10
pdf2image>=1.16.3
pandas>=2.0.0
"""

with open('requirements.txt', 'w') as f:
    f.write(requirements_content)