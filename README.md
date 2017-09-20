# Journal Citation Reports

## Version 1.1: 20/09/2017
## Version 1.0: 14/10/2016


Generate LaTeX/PDF reports of journal rankings from a CSV file downloaded from the Thomson Journal Citation Reports site. Puts titles from a chosen category into a table and marks each title with its quartile. Top 10% journals have their quartile label in bold. Separators are placed in the table to mark the quartile boundaries and different background colours are used for each quartile.

The python script jcr.py uses Jinja LaTeX template, jcr.tex and produces a .tex file whose filename is the journal category in question.

    usage: jcr.py [-h] [-p] [-f FONT] [-d] input
    
    positional arguments:
      input                 Name of a CSV file
    
    optional arguments:
      -h, --help            show this help message and exit
      -p, --pdf             Generate PDF files from LaTeX source
      -f FONT, --font FONT  Font for main text. Default is Helvetica Neue Light.
                            Remember to escape the spaces in multiword font names
                            (e.g., 'Times\ New\ Roman') or enclose in quotes
                            (e.g., 'Times New Roman').
      -d, --debug           Enable various print statements to help debug.
      
      