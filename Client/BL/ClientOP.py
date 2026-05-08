import logging
from customtkinter import *
import fpdf

# prepare Log file
LOG_FILE = '../Client LOG.log'
logging.basicConfig(filename=LOG_FILE,level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

#Writes a message to the log file and also prints it to the console.
def write_to_log(msg):
    logging.info(msg)
    print(msg)

#Generates a formatted PDF file from provided data and saves it to a user-selected directory.
def save_to_pdf(data):
    try:
        directory=open_directory_dialog(data['name'])
        if directory=="no directory":
            return False
        pdf = fpdf.FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", style="BU", size=16)
        pdf.set_text_color(44, 62, 80)
        pdf.multi_cell(0, 10, data['name'], border=0,align="C")

        pdf.set_font("Arial",size=14)
        pdf.set_text_color(74, 74, 74)
        pdf.multi_cell(0, 10, data['description'], align='J')

        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 10, data['data'], align='J')

        pdf.set_font("Helvetica", style="BU", size=16)
        pdf.set_text_color(44, 62, 80)
        pdf.multi_cell(0, 10, 'Nutrition', border=0,align="C")

        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 10, data['nutrition'], align='J')
        pdf.output(directory)
        return True
    except Exception as e:
        write_to_log(f"[Client_BL] Exception {e} while saving to pdf")
        return False

#Opens a file save dialog for the user to choose a location and filename for the PDF.
def open_directory_dialog(name):
    """Opens a directory dialog to select a folder."""
    directory_path = filedialog.asksaveasfile(
        title="Select a directory",
        initialdir="/",
        initialfile=name,
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    if directory_path:
        return directory_path.name
    else:
        return "no directory"

 # Truncates long text strings for UI display.
def shorten(text,max_len):
    if len(text) <= max_len:
        return text
    return text[:max_len-3] + "..."

