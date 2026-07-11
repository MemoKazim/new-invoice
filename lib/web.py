from lib.colors import bcolors as c
import lib.handler as h
import sys
import time
import json
import base64

CERTIFICATES = []

host = "https://new.e-taxes.gov.az"

REFRESH_BUFFER_SECONDS = 60

def _decodeTokenExp(session):
  """
  Decodes the current X-Authorization bearer JWT and returns its `exp` claim (unix seconds).
  Returns None if header missing or token malformed.
  """
  token = session.headers.get("X-Authorization", "")
  if not token.startswith("Bearer "):
    return None

  try:
    payload = token.split(" ")[1].split(".")[1]
    padded = payload + "=" * (-len(payload) % 4)
    claims = json.loads(base64.urlsafe_b64decode(padded))
    return claims.get("exp")
  except Exception:
    return None

def refreshTokenIfNeeded(certificate, session):
  """
  Re-issues the X-Authorization bearer token when it's close to expiring.
  The e-taxes portal keeps the underlying ASAN IMZA session alive independently of the
  short-lived (10 min) JWT, so calling chooseTaxpayer again silently mints a fresh token
  without requiring the user to re-confirm on their phone.
  `certificate`: previously selected certificate tuple (tin, name, taxpayerType)
  `session`: Session object
  """
  exp = _decodeTokenExp(session)

  if exp is None or time.time() < exp - REFRESH_BUFFER_SECONDS:
    return session

  print(f"{c.FG_YELLOW}[*] Access token about to expire. Refreshing session...{c.END}")
  session = getDashboard(certificate, session)
  return session

def AsanLogin(data, session):
  """
  This function sends POST request to asan login page.
  Required arguments:
  `data`: Dictionary data of required fields to POST request
  `session`: Session object
  """

  # Unpack data object to get phone and user id  
  phone = data['phone']
  userId = data['id']

  # Set custom headers
  headers = {
  "Content-Type":"application/json",
  "Referer":"https://new.e-taxes.gov.az/eportal/az/login/asan",
  "Sec-Fetch-Dest":"empty",
  "Sec-Fetch-Mode":"cors",
  "Sec-Fetch-Site":"same-origin",
  }

  # Create data payload
  data = {"phone":phone,"userId":userId}
  data = json.dumps(data)

  # Send POST request to specified endpoint
  r = session.post(host + "/api/po/auth/public/v1/asanImza/start", headers=headers, data=data)

  # Get token and set it to Session object
  try:
    token = r.headers['x-authorization']
    session.headers.update({"X-Authorization": f"Bearer {token}"})
  except:
    print(f"{c.FG_RED}[!] Incorrect login information. Exiting...{c.END}")
    sys.exit()

  # Inform user about action
  print(f"{c.FG_GREEN}[+] Logging in system via ASAN IMZA\n{c.FG_YELLOW}[*] Waiting for confirmation!{c.END}")
  # input(f"{c.FG_YELLOW}[*] Press Enter after conforming ASAN IMZA...{c.END}") # Remove manual checking

  tempHeader = {
    "Referer": "https://new.e-taxes.gov.az/eportal/az/verification/asan"
  }

  fail_count = 0
  # Check Asan Imza status by user action
  while True:
    try:
      # Send request to check asan imza status
      r = session.get(host + "/api/po/auth/public/v1/asanImza/status", headers=tempHeader)

      # If status is not successful send request to check again
      while not r.json()['successful']:
        # input(f"{c.FG_YELLOW}[*] Press Enter after confirming ASAN IMZA...{c.END}") # Remove manual checking
        r = session.get(host + "/api/po/auth/public/v1/asanImza/status", headers=tempHeader)
        time.sleep(3) # Remove manual checking
      break

    # Handle possible exceptions
    except Exception as e:
      fail_count+=1
      print(f"{c.FG_RED}[-] ASAN IMZA is not confirmed yet!{c.END}")
      time.sleep(4)

      r = session.get(host + "/api/po/auth/public/v1/asanImza/status", headers=tempHeader)

      if fail_count == 3:
        print(f"{c.FG_RED}[!] Something went wrong. Please try again. \nExiting program...{c.END}")
        sys.exit()
        break

  # Inform user about successful login
  print(f"{c.FG_GREEN}[+] Login Success!{c.END}")
  return session

def SVLogin(data):
  """
  This function sends POST request to Personal Identification login page.
  Required arguments:
  `data`: Dictionary data of required fields to POST request
  `session`: Session object
  """
  fin = data['fin']
  phone = data['phone']
  print(f"{c.FG_YELLOW}[*] This login functionality is not availbale currently.{c.END}")
  # TODO Handle this login
  pass

def KPSLogin(data):
  """
  This function sends POST request to Code/Password/Passphrase login page.
  Required arguments:
  `data`: Dictionary data of required fields to POST request
  `session`: Session object
  """
  usercode = data['usercode']
  code = data['code']
  password = data['password']
  print(f"{c.FG_YELLOW}[*] This login functionality is not availbale currently.{c.END}")
  # TODO Handle this login
  pass

def listCertificates(session):
  """
  This functions returns all certificates accoring login information
  `session`: Session object
  """
  # Get all certificates in json format
  r = session.get(host + "/api/po/auth/public/v1/asanImza/certificates")

  for cert in r.json()['certificates']:

    # If current certificate does not has access to invoices page just continue
    if not cert['hasAccess']:
      continue
    
    # Generate data accoring tax payer information
    if cert['taxpayerType'] == 'legal':
      name = cert['legalInfo']['name']
      tin = cert['legalInfo']['tin']
      CERTIFICATES.append((tin,name,cert['taxpayerType'],))
    if cert['taxpayerType'] == 'individual':
      name = cert['individualInfo']['name']
      tin = cert['individualInfo']['fin']
      CERTIFICATES.append((tin,name,cert['taxpayerType'],))
  
  # Return all cretificates available
  return CERTIFICATES

def getDashboard(certificate, session):
  """
  This function configures cookies to access dashboard page and returns session object
  `certificate`: Selected certificate data
  `session`: Session object
  """
  data = {}

  # Generate json data accoring to certificate choice
  if certificate[2] == "legal":
    data = {
      "ownerType": certificate[2],
      f"{certificate[2]}Tin": certificate[0]
    }

  if certificate[2] == "individual":
    data = {
      "ownerType": certificate[2],
      f"{certificate[2]}Fin": certificate[0]
    }

  # Set custom headers to send request
  headers = {
    'Content-Type': 'application/json',
    'Origin': 'https://new.e-taxes.gov.az',
    'Referer': 'https://new.e-taxes.gov.az/eportal/az/verification/companies',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Priority": "u=0, i",
  }

  # Send request to get cookie from server
  r = session.post(host + "/api/po/auth/public/v1/asanImza/chooseTaxpayer", json=data, headers=headers)

  # If request is not successful inform user and exit
  if not r.json()['successful']:
    print(f"{c.FG_RED}[!] Something went wrong. Please try again later{c.END}")
    sys.exit()
  
  # Set cookies to Session object and return it
  session.headers.update({'X-Authorization': f"Bearer {r.headers['x-authorization']}"})
  return session

def getInvoiceUrls(overheadChoice, fromDate, toDate, session, certificate):
  """
  This function returns all invoice api URLs according params.
  `overheadChoice`: it should be either "find.inbox" or "find.outbox"
  `fromDate`: "dd-mm-yyyy" formatted date object
  `toDate`: "dd-mm-yyyy" formatted date object
  `session`: Session object
  `certificate`: selected certificate tuple, needed to silently refresh the token on long fetches
  """
  URLS = []

  filter="""
{
  "sortBy": "creationDate",
  "sortAsc": true,
  "statuses": [
    "approved",
    "onApproval",
    "updateApproval",
    "updateRequested",
    "cancelRequested",
    "approvedBySystem",
    "onApprovalEdited",
    "canceled",
    "deletedBySystem",
    "deactivated",
    "cancelationRefused",
    "correctionRefused"
  ],
  "types": [
    "current",
    "corrected"
  ],
  "kinds": [
    "defaultInvoice",
    "agent",
    "resale",
    "recycling",
    "taxCodex163",
    "taxCodex177_5",
    "returnInvoice",
    "returnByAgent",
    "returnRecycled",
    "exportNoteInvoice",
    "exciseGoodsTransfer",
    "advanceInvoice"
  ],
  "serialNumber": null,
  "senderTin": null,
  "senderName": null,
  "productName": null,
  "productCode": null,
  "receiverTin": null,
  "receiverName": null,
  "creationDateFrom": "FROMDATE 00:00",
  "creationDateTo": "TODATE 23:59",
  "amountFrom": null,
  "amountTo": null,
  "offset": 0,
  "maxCount": 200,
  "actionOwner": null
}
  """

  # Use filter.json as template
  # with open("./json/filter.json", "r", encoding="UTF-8") as j:
  #   filter = j.read()

  # Convert string to dictionary data
  filter = json.loads(filter)

  # Set date range
  filter["creationDateFrom"] = f"{fromDate} 00:00"
  filter["creationDateTo"] = f"{toDate} 23:59"
  page=0

  # Get all URLs while hasMore parameter in json is true
  while True:

    # Refresh access token before it expires so long date ranges don't get cut off mid-fetch
    session = refreshTokenIfNeeded(certificate, session)

    # Set offset to not retrieve same invoices again
    filter["offset"] = page * filter["maxCount"]

    # Retrieve json invoce data
    r = session.post(host + f"/api/po/invoice/public/v2/invoice/{overheadChoice}", json=filter)

    # Format json data to generate URLs
    for item in r.json()['invoices']:
      invoiceUrl = f"{host}/api/po/invoice/public/v2/invoice/{item['id']}?sourceSystem={item['sourceSystem']}"
      URLS.append(invoiceUrl)
    
    # Go to the next page
    page += 1

    # Check whether in date rage left invoices
    if not r.json()['hasMore']:
      break
    
  return URLS

def getOverheads(URLS, session, filename, certificate):
  """
  This function generates CSV file accoring given URLS
  `URLS`: list of api URLs
  `session`: Session object which contains cookies
  `filename`: CSV filename to set
  `certificate`: selected certificate tuple, needed to silently refresh the token on long fetches
  """
  print(f"{c.FG_GREEN}[*] Retrieving data from server. Please wait.\n[*] This might take while")
  # Loop through each invoice URL and generate CSV report
  for invoice in URLS:
    # Refresh access token before it expires so large invoice counts don't fail mid-fetch
    session = refreshTokenIfNeeded(certificate, session)

    # Retrieve json data regarding invoice data
    r = session.get(invoice)

    # Parse it as inbox data and generate CSV
    h.parseInbox(r.json(), invoice, filename)

def logout(session):
  r = session.post(host + "/api/po/auth/public/v1/legacyLogout")
  if r.ok:
    print(f"{c.FG_GREEN}[+] Successfully logged out.{c.END}")
  
  session.cookies.clear()
  session.headers = {}
  print(f"{c.FG_GREEN}[+] Session terminated!{c.END}")
  session.close()