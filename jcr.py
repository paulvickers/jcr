#!/usr/bin/env python
#
# Script for taking .CSV downloads from Journal Citation Reports
# and formatting the lists as PDFs which each journal tagged with its quartile
# position.
#
# Paul Vickers, 2016.

import jinja2 # Required for templating 
import csv       # Required for reading CSV files
import sys		 # Required for system and interpreter functions
import os		 # Required for OS functions
import subprocess # Required for calling OS subprocesses
import argparse  # Required for the natty argument handling
import re        # Required for the RegEx searching (slicing and dicing the strings)
import datetime  # Required for date and time functions
import urllib    # Required for translating "%20" etc encoded strings in category title to unicode equivalents

# For skipping the last row of the CSV file which just has copyright info in it.
def skip_last(iterator):
    prev = next(iterator)
    for item in iterator:
        yield prev
        prev = item

def skip_footers(iterator):
	for item in iterator:
		if 'Copyright' not in item[0] and 'By exporting' not in item[0]:
			yield item
			
# Return to top of file and skip n header rows
def goto_top(file, iterator, n):
	file.seek(0)
	for i in range (n):
		next(iterator)


def main():		
	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("input", help="Name of a CSV file")	
	parser.add_argument("-p", "--pdf", action='store_true', default=False, 
                    help="Generate PDF files from LaTeX source")
	parser.add_argument("-f", "--font", action='store', default='Helvetica Neue Light',
                    help="Font for main text. Default is Helvetica Neue Light. Remember to escape the spaces in multiword font names (e.g., 'Times\ New\ Roman') or enclose in quotes (e.g., 'Times New Roman').")
	parser.add_argument("-d", "--debug", action='store_true', default=False,
                    help="Enable various print statements to help debug.")
	args = parser.parse_args()
	root = args.input	

	if args.debug:
		print "START"	
	env = jinja2.Environment(
	block_start_string = '%{',
	block_end_string = '%}',
	variable_start_string = '%{{',
	variable_end_string = '%}}',
	loader = jinja2.FileSystemLoader(os.path.abspath('.')))
	
	template = env.get_template("jcr.tex")
	if args.debug:
		print template
	# create a corresponding output directory
	outputDir = 'JCRReports'
	if args.debug:
		print outputDir
	if not os.path.exists(outputDir):
		os.mkdir (outputDir)
	templateVars = {}
	templateVars['filename'] = root
	templateVars['font'] = args.font	
	now = datetime.datetime.now()
	templateVars['date'] = now.strftime("%d/%m/%Y")
	with open(args.input, 'U') as infile:
		reader = csv.reader(infile)
		firstLine = next(reader)[0] # Read first line of file which contains category
		                            # First line looks like this:
		                            # "Journal Data Filtered By:  Selected JCR Year: 2015 Selected Editions: SCIE,SSCI Selected Categories: 'COMPUTER%20SCIENCE%2C%20ARTIFICIAL%20INTELLIGENCE' Selected Category Scheme: WoS",,,,,
		try: #Get category which is enclosed by '' and replace '%20' with ' ' and '%2C' with ',', '%26' with '\&'
# THIS IS THE SEXY REGEX SOLUTION
			# Use the urllib.unquote to replace the URL encoded characters
			# such as '%20' with their unicode equivalent (' ')
			title = urllib.unquote(re.search(".+\'(.+?)\'.+", firstLine).group(1))
			# Then replace any '&' with '\&' for passing through to LaTeX
			title = title.replace('&', '\\&')
			
			# Doing it without urllib. But you need to remember to cater for each
			# URL-encoded character you are going to encounter
			#title = re.search(".+\'(.+?)\'.+", firstLine).group(1).replace('%20', ' ').replace('%2C',',').replace('%26','\\&')
			
# END OF REGEX
# THIS IS THE LONGER WAY TO DO IT
#			catStart = title.find ("'")+ 1
#			title = title[catStart:]
#			catEnd = title.find("'")
#			title = title[:catEnd].replace('%20', ' ').replace('%2C',':').replace('%26','\\&')
# END OF LONG WAY			
		except AttributeError:
			# couldnt find category
			title = ''
		if args.debug:
			print title
		# Get year
		templateVars['year'] = re.search(".+JCR Year: ([0-9]+).+", firstLine).group(1)
		if args.debug:
			print templateVars['year']
		#Get column headings
		cols = next(reader)
		templateVars['col1'] = 'Quartile'
		templateVars['col2'] = cols[0]
		templateVars['col3'] = '\%'
		templateVars['col4'] = cols[1]
		templateVars['col5'] = 'Impact Factor'
		templateVars['col6'] = '5-yr IF'
		
#		outfil = open('JCRReport.txt', 'w')

# Read in each journal's details
		journals = []
		if args.debug:
			print "Num lines: " + str(reader.line_num)
		# num journals:
		numJournals = sum(1 for row in reader) -2 #subtract two headers, footers already discarded
		goto_top(infile, reader, 2)
		if args.debug:
			print "Num Journals: " + str(numJournals)
		#for row in skip_last(reader):
		for row in skip_footers(reader):
		#for row in reader:
		    # col[0] is rank, [1] is title, [2] is total cites (ignore) [3] is JIF, [4]
		    # is 5-year JIF
			percentage = "%.2f" % (float(row[0]) / numJournals *100)
			journal = ' & '.join((row[0],percentage, row [1].replace('&', '\&'), row[3], row[4])) + '\\\\'
			if args.debug:
				print percentage + '%'
				print journal
			journals.append(journal)
				
# Now work out quartile and top 10% info and add it.
	tempJournals = []
	top10 =numJournals /10
	Q1 = numJournals / 4
	Q2 = numJournals / 4 * 2
	Q3 = numJournals /4 * 3

	if args.debug:
		print top10, Q1, Q2, Q3
	ctr = 0
	for journal in journals:
		ctr += 1
		rank = float(journal[:journal.find(' ')])
		if rank <= top10:
			journal = '\\rowcolor{DarkSeaGreen1}\\textbf{Q1} & ' + journal
		elif rank <= Q1:
			journal = '\\rowcolor{DarkSeaGreen2}Q1 & ' + journal
		elif rank <= Q2:
			journal = '\\rowcolor{LightGoldenrod1} Q2 & ' + journal
		elif rank <= Q3:
			journal = '\\rowcolor{LightSalmon1}Q3 & ' + journal
		else:
			journal = '\\rowcolor{LightSalmon2}Q4 & ' + journal
		tempJournals.append(journal)
		if ctr in [Q1, Q2, Q3]:
			tempJournals.append('\midrule')
	journals = tempJournals
	tempjournals = []
			

# Write everything out
	filnam = title.replace(', ', '_').replace(' \\& ', '_').replace(' ','_')
	outfile = filnam + '.tex'
	path = os.path.join(outputDir, outfile)	
	if args.debug:
		print path
	with open(path, mode="w") as outfil:
		outputString = '\n'.join(journals)
		templateVars['title'] = title
		templateVars ['rankings'] = outputString
		outfil.write(template.render(templateVars))
	outfil.close()	
	
# Generate PDFs
	if args.pdf:
		if args.debug:
			print 'Generating PDFs'
		
		filroot = os.path.join(outputDir, filnam)
		if args.debug:
			print filroot
		subprocess.check_output(['/Library/TeX/texbin/xelatex', "".join((filroot, ".tex"))])

		subprocess.check_output(['mv', "".join((filnam, ".pdf")), outputDir])
		subprocess.check_output(['rm', "".join((filnam, ".aux"))])
		subprocess.check_output(['rm', "".join((filnam, ".log"))])	   
	if args.debug:
		print "DONE"
	
main()