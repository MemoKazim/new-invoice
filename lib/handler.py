from lib.colors import bcolors as c
from openpyxl import Workbook
import lib.validate as v
import pandas as pd
import importlib
import os

def checkLib():
  """
  This function checks whether required library is in end system
  """
  try:
      importlib.import_module('pandas')
  except:
      os.system("pip install pandas")
  try:
      importlib.import_module('requests')
  except:
      os.system("pip install requests")
  try:
      importlib.import_module('openpyxl')
  except:
      os.system("pip install openpyxl")

def getAsanLogin():
  """
  This function handles user input and requires data which will be required in Asan Login page
  """

  # Inform user
  print(f"{c.FG_GREEN}[+] Getting Asan Login requirements{c.END}")
  print(f"{c.FG_YELLOW}[*] Please enter ASAN Phone number in {c.BOLD}+994XXXXXXXXX{c.END + c.FG_YELLOW} format and User ID. e.g.(+994123456789):\n")

  # Get Phone Number and validate until valid
  phone = input(f"{c.FG_YELLOW}Phone: {c.END}")
  while not v.validatePhone(phone):
    print(f"{c.FG_RED}[!] Invalid Phone Number! Try again. {c.END}")
    phone = input(f"{c.FG_YELLOW}Phone:{c.END}")

  # Get UserID and validate until valid
  id = input(f"{c.FG_YELLOW}User ID: {c.END}")
  while not v.validateID(id):
    print(f"{c.FG_RED}[!] Invalid ID! Try again. {c.END}")
    id = input(f"{c.FG_YELLOW}User ID:{c.END}")
  
  return {"phone":phone, "id":id}

def getSVLogin():
  """
  This function handles user input and requires data which will be required in Personal Identification login page
  """
  print(f"{c.FG_GREEN}[+] Getting SV requirements{c.END}")
  pass

def getKPSLogin():
  """
  This function handles user input and requires data which will be required in Code/Password/Passphrase login page
  """
  print(f"{c.FG_GREEN}[+] Getting KPS requirements{c.END}")
  pass

def signInHandler():
  """
  This function handles user input for login type.
  """

  # Inform User about login types
  print(f"{c.FG_YELLOW}[+] Please Select SignIn option from list below!{c.FG_GREEN}")
  print(f"""
  1. Kod / Parol / Sifre  [Currently Unavailable]
  2. Sexsiyyet Vesiqesi   [Currently Unavailable]
  3. Asan Imza {c.END}
  """)

  # Get login type and validate until valid
  signInChoice = input(f"{c.FG_YELLOW}[*] Option: {c.END}")
  while True:
    try:
      if int(signInChoice) >=1 and int(signInChoice) <= 3:
        # For temporary period block type 1 and type 2 login variant
        if int(signInChoice) != 3:
          print(f"{c.FG_YELLOW}[-] This option is currently unavailable please choose other option!{c.END}")
          raise Exception
        break
      else:
        raise Exception
    except:
      print(f"{c.FG_RED}[-] Incorrect option! Try again{c.END}")
      signInChoice = input(f"{c.FG_YELLOW}[*] Option: {c.END}")

  
  return signInChoice

def overheadHandler():
  """
  This function handles user input for Overhead Choice
  """

  # Inform User about available options
  print(f"{c.FG_YELLOW}[+] Please Select overhead status!{c.FG_GREEN}")
  print(f"""
  1. Gelen qaimeler
  2. Gonderilen qaimeler{c.END}
  """)

  # Get overhead choice and validate until valid
  overheadChoice = input(f"{c.FG_YELLOW}[*] Option: {c.END}")
  while True:
    try:
      if int(overheadChoice) >=1 and int(overheadChoice) <= 2:
        break
      else:
        raise Exception
    except:
      print(f"{c.FG_RED}[-] Incorrect option! Try again{c.END}")
      overheadChoice = input(f"{c.FG_YELLOW}[*] Option: {c.END}")
  return overheadChoice

def dateHandler():
  """
  This function handles user input for getting valid date range (fromDate & toDate)
  """

  # Inform User for valid date format
  print(f"{c.FG_YELLOW}[*] Please enter Date range in {c.BOLD}dd-mm-yyyy{c.END + c.FG_YELLOW} format. e.g. (30-12-2024)\n")

  # Get fromDate value and validate until valid
  fromDate = input(f"{c.FG_YELLOW}From: {c.END}")
  while not v.validateDate(fromDate):
    print(f"{c.FG_RED}[-] Incorrect fromDate value! Try again!{c.END}\n")
    fromDate = input(f"{c.FG_YELLOW}From: {c.END}")

  # Get toDate value and validate until valid
  toDate = input(f"{c.FG_YELLOW}To: {c.END}")
  while not v.validateDate(toDate):
    print(f"{c.FG_RED}[-] Incorrect toDate value! Try again!{c.END}\n")
    toDate = input(f"{c.FG_YELLOW}To: {c.END}")
  
  return fromDate, toDate

def certificateHandler(certificates):
  """
  This function handles user input for cretificate choice.
  `certificates`: list of tuple data which contains certificates
  """

  # Inform User about available certificates
  print(f"{c.FG_YELLOW}[*] Please select tax payer certificate below!{c.FG_GREEN}\n")
  count = 1
  for cert in certificates:
    print(f'{count}. {cert[0]} - {cert[1]}')
    count+=1
  print(f"""{c.END}""", end='')

  # Validate selected certificate option
  certificateChoice = input(f"\n{c.FG_YELLOW}[*] Option: {c.END}")
  while True:
    try:
      if int(certificateChoice) > 0 and int(certificateChoice) <= len(certificates):
        break
      else:
        raise Exception
    except:
      print(f"{c.FG_RED}[-] Incorrect option! Try again{c.END}")
      certificateChoice = input(f"{c.FG_YELLOW}[*] Option: {c.END}")
  return int(certificateChoice)

def parseInbox(json, url, filename):
  """
  This function parses json data into csv readable rows, and writes each row into filname given.
  `json`: JSON data which retrieved from invoice api URL
  `url`: This string will be used for "reference" column in CSV file
  `filename`: Filename for write data into
  """

  # Open file to write into it
  with open(f"tmp/{filename}", "a", encoding="UTF-8") as r:

    # Iterate through all items in single invoice and parse data for future use
    for item in json['items']:
      productName = item['productName'].replace(",","，").replace("\n", ".")
      productCode = item['productGroup']['code'].replace(",","，").replace("\n", ".")
      barcode     = item['barcode']
      unit        = item['unit'].replace(",","，").replace("\n", ".")
      quantity    = float(item['quantity'])
      pricePerUnit= float(item['pricePerUnit'])
      costAmount  = float(pricePerUnit * quantity)
      exciseRate  = float(item['exciseRate'])
      excise      = float(item['excise'])
      cost        = float(costAmount + excise)
      vat18       = float(item['vat18'])
      vat0        = float(item['vat0'])
      vatFree     = float(item['vatFree'])
      exempt      = float(item['exempt'])
      vatCost     = float(vat18 * 0.18)
      roadTax     = float(item['roadTax'])
      finalPrice  = float(cost + vatCost + roadTax)
    
      # Fix unclosed values
      comment = json["invoiceComment"].replace(",","，").replace("\n", ".")
      if comment.count('"') % 2 != 0:
        comment += '"'
      if comment.count("'") % 2 != 0:
        comment += "'"

      # Define row for nice format writing in csv file
      row = {
        "createdAt"   : ' '.join(map(str,json['createdAt'].split("T"))),
        "senderName"  : json['sender']['name'],
        "senderTIN"   : json['sender']['tin'],
        "receiverName": json['receiver']['name'],
        "receiverTIN" : json['receiver']['tin'],
        "comment"     : comment,
        "serialNumber": json['serialNumber'],
        "status"      : json['status'],
        "productName" : productName,
        "productCode" : productCode,
        "barcode"     : barcode,
        "unit"        : unit,
        "quantity"    : quantity,
        "pricePerUnit": pricePerUnit,
        "costAmount"  : costAmount,
        "exciseRate"  : exciseRate,
        "excise"      : excise,
        "cost"        : cost,
        "vat18"       : vat18,
        "vat0"        : vat0,
        "vatFree"     : vatFree,
        "exempt"      : exempt,
        "vatCost"     : vatCost,
        "roadTax"     : roadTax,
        "finalPrice"  : finalPrice,
        "reference"   : f"https://new.e-taxes.gov.az/eportal/az/invoice/view/{url.split("/")[-1].replace('sourceSystem', 'source')}",
      }
      print(row["reference"])
      # Write data into file
      r.write(f"{row["createdAt"]},{row["senderName"]},{row["senderTIN"]},{row["receiverName"]},{row["receiverTIN"]},{row["comment"]},{row["serialNumber"]},{row["status"]},{row["productName"]},{row["productCode"]},{row["barcode"]},{row["unit"]},{row["quantity"]},{row["pricePerUnit"]},{row["costAmount"]},{row["exciseRate"]},{row["excise"]},{row["cost"]},{row["vat18"]},{row["vat0" ]},{row["vatFree"]},{row["exempt" ]},{row["vatCost"]},{row["roadTax"]},{row["finalPrice"]},{row["reference"]}\n")

def setCsvHeaders(filename, headers):
  """
  This funtion sets headers which given to filename.
  `filename`: CSV filename
  `headers`: String data of headers
  """
  # Open file and set csv headers
  with open(f"tmp/{filename}", "w", encoding="UTF-8") as mf:
    mf.write(headers)

  # Inform user about action
  print(f"{c.FG_GREEN}[+] File headers has been set! {c.END}")

def convertToXlsx(csvDirectory, filename):
  """
  This function generates excel file using csv data.
  `csvDirectory`: folder name of contained csv files
  `filename`: Excel export filename
  """
  # Inform User about action
  print(f"{c.FG_GREEN}[+] Generating excel report please wait...")

  # Reform filename to xlsx extention
  filename = filename.split(".")[0] + ".xlsx"

  # Generate Excel file 
  with pd.ExcelWriter(f"reports/{filename}", engine='openpyxl') as writer:
    
    # Get all csv files from given directory path
    for filename in os.listdir(csvDirectory):

      # Check if file extention is csv
      if filename.endswith('.csv'):
        filePath = os.path.join(csvDirectory, filename)
        df = pd.read_csv(filePath)

        # Set excel sheet name
        sheetName = "Report"
        df.to_excel(writer, sheet_name=sheetName, index=False, header=True)
  
  # Inform User about generation
  print(f"{c.FG_GREEN}[+] Generated excel file under ./reports/ path{c.END}")

def cleanTmp():
  """
  This function cleans ./tmp/ folder to avoid report collusion.
  """
  for file in os.listdir("./tmp"):
    os.system(f"del tmp\\{file}")
  
  # Inform User about action
  print(f"{c.FG_GREEN}[+] Tmp directory cleaned{c.END}")

def fileOpenerHandler(filename):
  """
  This function asks user whether open generated file or not
  `filename`: Filename to open
  """

  # Ask user if he/she want to open file?
  user_input = input(f"{c.FG_YELLOW}[*] Do you want to open report file? [n/Y]: ")

  # If not valid just pass
  if user_input not in ["y", "Y", "", "n", "N"]:
    print(f"{c.FG_YELLOW}[!] Incorrect option. File opening aborted. \nHave a nice day :) {c.END}")
  
  # If User wants to open file
  if user_input in ["y", "Y", ""]:
    print(f"{c.FG_GREEN}[+] Opening file...\nHave a nice day :) {c.END}")
    os.system("explorer reports")
    os.system(f"start reports\\{filename.split('.')[0]+".xlsx"}")
  
  # If User does not want to open file
  if user_input in ["n", "N"]:
    print(f"{c.FG_YELLOW}[-] File opening aborted. Have a nice day :) {c.END}")
