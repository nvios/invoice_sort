# The following script is a stripped-down version of the production code 
# and it was used in the preliminary stages as a prototype for the actual application. 
# Any sensitive information has been replaced due to confidentiality clauses.

import os
import pandas as pd
import fnmatch
import math
import shutil
from PyPDF2 import PdfFileReader, PdfFileWriter

# Invoice pre-processing

directory = 'Files to Process'
document = 0

for file in os.listdir(directory):
    if file.endswith(".pdf"):
        path = 'Files to Process/'+file
        fname = os.path.splitext(os.path.basename(path))[0]
        pdf_reader = PdfFileReader(path)
        pdf_writer = PdfFileWriter()
        if pdf_reader.getNumPages() == 1:
            pdf_writer.addPage(pdf_reader.getPage(0))
            pdf_writer.write(open('Processed Files/'+file, 'wb'))
        else:    
            pages = int(pdf_reader.getNumPages()/2)    
            for page in range(pages):
                pdf_writer.addPage(pdf_reader.getPage(page+pages))
            pdf_writer.write(open('Processed Files/'+file, 'wb'))

        os.remove(path)
        document += 1
        print('\n\n',document,'- Copy created for: \n\n>>> '+file+ ' <<<')

print('\n\nYour',document,'files have been successfully processed and are ready for sorting.\n\n')  

# Invoice sorting 

for file in os.listdir('Master'):
    if file.endswith('.xlsx') or file.endswith('.xls'):
        path = 'Master/'+file 
        df = pd.read_excel(path, header=2, usecols=[0,7,23,24])
        counter = 0
        for i in range(len(df.index)):
            inv_type = df.iloc[i,0]        
            sold_to = df.iloc[i,1]
            invoice = str(df.iloc[i,2])
            amount = df.iloc[i,3]
            if amount == 0:
                print(counter,'Null amount')
                counter += 1
                continue
            elif inv_type == 'CANCELLED':
                counter += 1
                for x in os.listdir('Processed Files'):
                    if fnmatch.fnmatch(x, '*'+invoice+'*'):
                        if not os.path.exists('Invoices/Cancelled Invoices'):
                            os.makedirs('Invoices/Cancelled Invoices') 
                        try:
                            os.rename('Processed Files/'+x, 'Invoices/Cancelled Invoices/'+x)
                        except Exception:
                            pass
                        print(counter,'Invoice cancelled:',x)
                continue        
            elif math.isnan(sold_to):
                counter += 1
                for x in os.listdir('Processed Files'):
                    if fnmatch.fnmatch(x, '*'+invoice+'*'):
                        if not os.path.exists('Invoices/No Sold To'):
                            os.makedirs('Invoices/No Sold To') 
                        try:
                            os.rename('Processed Files/'+x, 'Invoices/No Sold To/'+x)
                        except Exception:
                            pass
                print(counter,'No sold_to number:',invoice)                
                continue
            else:
                sold = str(int(sold_to))
                f = open('Master/Folder List.txt', 'r', errors='ignore').read().split('\n')
                for x in os.listdir('Processed Files'):
                    if fnmatch.fnmatch(x, '*'+invoice+'*'):
                        for line in f:
                            if fnmatch.fnmatch(line, '*'+sold+'*'):
                                folder = line
                                if not os.path.exists('Invoices/'+folder):
                                    os.makedirs('Invoices/'+folder) 
                                try:
                                    os.rename('Processed Files/'+x, 'Invoices/'+folder+'/'+x)
                                except Exception:
                                    pass
                                      
                                print(counter, 'Folder sorted', folder)
                counter += 1
    
        print(len(df.index)) 
        if counter == len(df.index):
            print('\n\nProcess completed with success.\n\n')

# Reset working directories

def reset_folders():
    for file in os.listdir('Master'):
        if file.endswith(".xlsx") or file.endswith(".xls"):
            os.remove('Master/'+file)
            print(file+', has been successfully removed.')

    for file in os.listdir('Invoices'):
        if file.endswith(".txt") or file.endswith(".pdf"):
            os.remove('Invoices/'+file)
            print(file+', has been successfully removed.')     

    for file in os.listdir('Invoices'):
        try:
            shutil.rmtree('Invoices/'+file)
            print(file+', has been successfully removed.') 
        except:
            print('File Skipped. Make sure the file is not in use') 
