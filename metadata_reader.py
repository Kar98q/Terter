import streamlit as st
from PIL import Image
from PIL.ExifTags import TAGS
import pdfplumber
import olefile
from docx import Document
import os
import pandas as pd

# Fungsi untuk membaca metadata gambar
def get_image_metadata(file_path):
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        metadata = {}
        
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                metadata[tag] = value
        
        # Informasi dasar gambar
        metadata["Format"] = image.format
        metadata["Mode"] = image.mode
        metadata["Size"] = image.size
        
        return metadata
    except Exception as e:
        return {"Error": str(e)}

# Fungsi untuk membaca metadata PDF
def get_pdf_metadata(file_path):
    try:
        metadata = {}
        with pdfplumber.open(file_path) as pdf:
            metadata["Pages"] = len(pdf.pages)
            if pdf.metadata:
                metadata.update(pdf.metadata)
        
        # Ukuran file
        metadata["File Size"] = f"{os.path.getsize(file_path) / 1024:.2f} KB"
        
        return metadata
    except Exception as e:
        return {"Error": str(e)}

# Fungsi untuk membaca metadata dokumen Office (docx)
def get_docx_metadata(file_path):
    try:
        doc = Document(file_path)
        metadata = {
            "Author": doc.core_properties.author,
            "Created": doc.core_properties.created,
            "Modified": doc.core_properties.modified,
            "Last Modified By": doc.core_properties.last_modified_by,
            "Revision": doc.core_properties.revision,
            "Title": doc.core_properties.title,
            "Subject": doc.core_properties.subject,
            "Keywords": doc.core_properties.keywords,
            "File Size": f"{os.path.getsize(file_path) / 1024:.2f} KB"
        }
        return {k: v for k, v in metadata.items() if v is not None}
    except Exception as e:
        return {"Error": str(e)}

# Fungsi untuk membaca metadata dokumen Office lama (doc)
def get_doc_metadata(file_path):
    try:
        if not olefile.isOleFile(file_path):
            return {"Error": "Not a valid OLE file"}
        
        ole = olefile.OleFileIO(file_path)
        metadata = {}
        
        # Summary Information
        if ole.exists('\x05SummaryInformation'):
            si = ole.getproperties('\x05SummaryInformation')
            mapping = {
                'title': 'Title',
                'subject': 'Subject',
                'author': 'Author',
                'keywords': 'Keywords',
                'comments': 'Comments',
                'last_saved_by': 'Last Saved By',
                'create_time': 'Created',
                'last_saved_time': 'Modified',
            }
            
            for ole_prop, display_name in mapping.items():
                if ole_prop in si:
                    metadata[display_name] = si[ole_prop]
        
        # Document Summary Information
        if ole.exists('\x05DocumentSummaryInformation'):
            dsi = ole.getproperties('\x05DocumentSummaryInformation')
            if 'company' in dsi:
                metadata['Company'] = dsi['company']
        
        metadata["File Size"] = f"{os.path.getsize(file_path) / 1024:.2f} KB"
        ole.close()
        return metadata
    except Exception as e:
        return {"Error": str(e)}

# Fungsi utama aplikasi Streamlit
def main():
    st.title("📝 Aplikasi Pembaca Metadata File")
    st.write("Unggah file untuk melihat metadata-nya (Gambar, PDF, DOCX, DOC)")
    
    uploaded_file = st.file_uploader(
        "Pilih file", 
        type=['jpg', 'jpeg', 'png', 'pdf', 'docx', 'doc']
    )
    
    if uploaded_file is not None:
        # Simpan file sementara
        file_path = f"temp_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.subheader(f"Metadata untuk: {uploaded_file.name}")
        
        # Tentukan jenis file dan baca metadata
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_ext in ('.jpg', '.jpeg', '.png'):
            metadata = get_image_metadata(file_path)
            if "Error" not in metadata:
                st.image(uploaded_file, caption="Preview Gambar", use_column_width=True)
        elif file_ext == '.pdf':
            metadata = get_pdf_metadata(file_path)
        elif file_ext == '.docx':
            metadata = get_docx_metadata(file_path)
        elif file_ext == '.doc':
            metadata = get_doc_metadata(file_path)
        else:
            metadata = {"Error": "Format file tidak didukung"}
        
        # Tampilkan metadata
        if "Error" in metadata:
            st.error(metadata["Error"])
        else:
            # Konversi ke DataFrame untuk tampilan yang lebih rapi
            df = pd.DataFrame(list(metadata.items()), columns=["Property", "Value"])
            st.dataframe(df)
        
        # Hapus file sementara
        os.remove(file_path)

if __name__ == "__main__":
    main()
