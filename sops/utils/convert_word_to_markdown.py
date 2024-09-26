import docx
import re
from typing import List
import re

def convert_table_to_markdown(table: docx.table.Table) -> str:
    """
    Convert a docx table to Markdown format.

    Args:
        table (docx.table.Table): A table object from the python-docx library.

    Returns:
        str: A string representation of the table in Markdown format.
    """
    md_table: List[str] = []
    for i, row in enumerate(table.rows):
        # Convert each cell to text and join with pipe symbols
        md_row: List[str] = [cell.text.strip() for cell in row.cells]
        md_table.append('| ' + ' | '.join(md_row) + ' |')
        
        if i == 0:  # After the header row, add a separator
            md_table.append('| ' + ' | '.join(['---' for _ in row.cells]) + ' |')
    
    return '\n'.join(md_table)

def convert_word_to_markdown(docx_file: str) -> str:
    """
    Convert a Word document to Markdown format.

    This function reads a .docx file and writes its content to a .md file,
    converting the formatting to Markdown syntax.

    Args:
        docx_file (str): Path to the input .docx file.
        markdown_file (str): Path to the output .md file.
    """
    # Open the Word document
    doc: docx.Document = docx.Document(docx_file)

    # Open a new file to write the Markdown content
    result: str = ""
    for element in doc.element.body:
        if isinstance(element, docx.oxml.text.paragraph.CT_P):  # It's a paragraph
            para: docx.text.paragraph.Paragraph = docx.text.paragraph.Paragraph(element, doc)
            if para.style and para.style.name.startswith('Heading'):
                # Convert headings
                level: int = int(para.style.name[-1])
                result +='#' * level + ' ' + para.text + '\n\n'
            elif para.style and para.style.name.startswith('List Bullet'):
                # Convert bullet points
                result +='- ' + para.text + '\n'
            else:
                # Convert regular paragraphs and handle inline formatting
                text: str = para.text
                # Escape underscores
                text = re.sub(r'(\w+)(\_)(\w+)', r'\1\\_\3', text)
                
                for run in para.runs:
                    if run.bold:
                        text = text.replace(run.text, f'**{run.text}**')
                    if run.italic:
                        text = text.replace(run.text, f'*{run.text}*')
                
                result +=text + '\n\n'
        
        elif isinstance(element, docx.oxml.table.CT_Tbl):  # It's a table
            table: docx.table.Table = docx.table.Table(element, doc)
            result +=convert_table_to_markdown(table) + '\n\n'

    return result
