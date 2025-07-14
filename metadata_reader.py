import streamlit as st
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import pdfplumber
import olefile
from docx import Document
import os
import pandas as pd
from datetime import datetime

# Try to import folium for mapping, but make it optional
try:
    import folium
    from streamlit_folium import folium_static
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

def clean_metadata_value(value):
    """Clean metadata values for safe display"""
    if isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, bytes):
        try:
            return value.decode('utf-8', errors='replace')
        except:
            return str(value)
    elif isinstance(value, datetime):
        return value.isoformat()
    elif value is None:
        return None
    else:
        try:
            return str(value)
        except:
            return "Unserializable value"

def get_gps_info(exif_data):
    """Extract GPS info from EXIF data"""
    if not exif_data:
        return {}
    
    gps_info = {}
    for key, value in exif_data.items():
        tag = TAGS.get(key, key)
        if tag == "GPSInfo" and isinstance(value, dict):
            for t in value:
                sub_tag = GPSTAGS.get(t, t)
                gps_info[sub_tag] = clean_metadata_value(value[t])
    return gps_info

def convert_to_degrees(value):
    """Convert GPS coordinates to decimal degrees"""
    try:
        if isinstance(value, tuple):
            d, m, s = value
            return d + (m / 60.0) + (s / 3600.0)
        elif isinstance(value, (int, float)):
            return float(value)
        else:
            return None
    except:
        return None

def get_gps_coordinates(gps_info):
    """Get latitude and longitude from GPSInfo"""
    try:
        gps_latitude = gps_info.get('GPSLatitude')
        gps_latitude_ref = gps_info.get('GPSLatitudeRef', 'N')
        gps_longitude = gps_info.get('GPSLongitude')
        gps_longitude_ref = gps_info.get('GPSLongitudeRef', 'E')

        if gps_latitude and gps_longitude:
            lat = convert_to_degrees(gps_latitude)
            lon = convert_to_degrees(gps_longitude)
            
            if lat is not None and lon is not None:
                if gps_latitude_ref.upper() != 'N':
                    lat = -lat
                if gps_longitude_ref.upper() != 'E':
                    lon = -lon
                return lat, lon
    except Exception as e:
        st.warning(f"Error processing GPS coordinates: {str(e)}")
    return None

def show_gps_location(lat, lon):
    """Display GPS location with available methods"""
    st.subheader("📍 Lokasi GPS")
    st.write(f"Koordinat: {lat:.6f}, {lon:.6f}")
    
    # Create Google Maps link
    google_maps_url = f"https://www.google.com/maps?q={lat},{lon}"
    st.markdown(f"[Buka di Google Maps]({google_maps_url})")
    
    # Show map if folium is available
    if FOLIUM_AVAILABLE:
        try:
            m = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker(
                [lat, lon],
                tooltip="Lokasi Foto",
                popup=f"Koordinat: {lat:.6f}, {lon:.6f}"
            ).add_to(m)
            folium_static(m)
        except Exception as e:
            st.warning(f"Failed to create map: {str(e)}")
    else:
        st.warning("Fitur peta tidak tersedia (folium tidak terinstall)")

def get_image_metadata(file_path):
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        metadata = {}
        
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                metadata[tag] = clean_metadata_value(value)
        
        # Basic image info
        metadata["Format"] = image.format
        metadata["Mode"] = image.mode
        metadata["Size"] = str(image.size)
        
        # Extract GPS info if available
        if exif_data and 34853 in exif_data:  # 34853 is GPSInfo tag
            gps_info = get_gps_info(exif_data)
            metadata["GPSInfo"] = gps_info
            
            coords = get_gps_coordinates(gps_info)
            if coords:
                metadata["Latitude"] = coords[0]
                metadata["Longitude"] = coords[1]
        
        return metadata
    except Exception as e:
        return {"Error": str(e)}

# [Keep all the other functions (get_pdf_metadata, get_docx_metadata, get_doc_metadata) 
# exactly the same as in the previous version]

def main():
    st.title("📝 Aplikasi Pembaca Metadata File")
    st.write("Unggah file untuk melihat metadata-nya (Gambar, PDF, DOCX, DOC)")
    
    if not FOLIUM_AVAILABLE:
        st.warning("Fitur peta tidak tersedia. Untuk menampilkan peta, install folium dengan: pip install folium streamlit-folium")
    
    uploaded_file = st.file_uploader(
        "Pilih file", 
        type=['jpg', 'jpeg', 'png', 'pdf', 'docx', 'doc']
    )
    
    if uploaded_file is not None:
        file_path = f"temp_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.subheader(f"Metadata untuk: {uploaded_file.name}")
        
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_ext in ('.jpg', '.jpeg', '.png'):
            metadata = get_image_metadata(file_path)
            if "Error" not in metadata:
                st.image(uploaded_file, caption="Preview Gambar", use_container_width=True)
                
                if "Latitude" in metadata and "Longitude" in metadata:
                    show_gps_location(metadata["Latitude"], metadata["Longitude"])
        elif file_ext == '.pdf':
            metadata = get_pdf_metadata(file_path)
        elif file_ext == '.docx':
            metadata = get_docx_metadata(file_path)
        elif file_ext == '.doc':
            metadata = get_doc_metadata(file_path)
        else:
            metadata = {"Error": "Format file tidak didukung"}
        
        if "Error" in metadata:
            st.error(metadata["Error"])
        else:
            df = pd.DataFrame(list(metadata.items()), columns=["Property", "Value"])
            
            # Remove coordinates from table if they're shown separately
            if "Latitude" in df['Property'].values and "Longitude" in df['Property'].values:
                df = df[~df['Property'].isin(['Latitude', 'Longitude', 'GPSInfo'])]
            
            df['Value'] = df['Value'].apply(lambda x: clean_metadata_value(x))
            st.table(df)
        
        os.remove(file_path)

if __name__ == "__main__":
    main()
