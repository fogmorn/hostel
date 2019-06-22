#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# "xhtml2pdf" на данный момент (08-2016) не поддерживается (с 2016-06-05).
# Возможно, стоит перейти на "WeasyPrint".

import cgi
import sha
import time
from xhtml2pdf import pisa


def main():
    f = cgi.FieldStorage()

    if f.has_key("template_name"):
        template = f["template_name"].value

    file = open(template+'.html', 'r')

    source_html = eval(file.read())

    output_filename = sha.new(repr(time.time())).hexdigest()+'.pdf'

    pisa.showLogging()
    convertHtmlToPdf(source_html, output_filename)

    print "Content-type: text/plain\n"
    print output_filename


# Define your data
def convertHtmlToPdf(source_html, output_filename):
    # Open output file for writing (truncated binary)
    result_file = open('statements/'+output_filename, "w+b")

    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(
                     source_html,
                     dest=result_file)

    # Close output file
    result_file.close()

    return

if __name__== "__main__":
    main()
