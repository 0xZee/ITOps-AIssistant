import PyPDF2
import tempfile
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

def process_pdf(pdf_path):
    """
    Extract text content from a PDF file
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        list: List of strings containing the text content of each page
    """
    try:
        pdf_content = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from each page
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                if text:
                    # Add page number information
                    pdf_content.append(f"Page {page_num + 1}: {text}")
        
        return pdf_content
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")

def display_pdf(pdf_path):
    """
    Display a PDF in the Streamlit sidebar using streamlit-pdf-viewer
    
    Args:
        pdf_path (str): Path to the PDF file
    """
    try:
        # Display the PDF with dimensions 200x100
        #pdf_viewer(pdf_path, width='90%', height=200)
        pdf_viewer(pdf_path, width=300, height=380)
    except Exception as e:
        pass
