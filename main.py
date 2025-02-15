from lib.colors import bcolors as c
from lib.banner import banner
import lib.handler as h
import lib.web as w
import requests
import time
import sys
import os

session = requests.Session()
session.headers.update({
  "Host":"new.e-taxes.gov.az",
  "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
  "Accept":"application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
  "Origin":"https://new.e-taxes.gov.az",
  "Accept-Language":"en-US,en;q=0.5",
  "Upgrade-Insecure-Requests":"1",
  "Sec-Fetch-Dest":"document",
  "Sec-Fetch-Mode":"navigate",
  "Sec-Fetch-Site":"none",
  "Sec-Fetch-User":"?1",
  "Priority":"u=0, i",
  "Te":"trailers",
  "Connection":"keep-alive",
})

singInOptions = {
  "1": h.getKPSLogin,
  "2": h.getSVLogin,
  "3": h.getAsanLogin
}

signIn = {
  "1": w.KPSLogin,
  "2": w.SVLogin,
  "3": w.AsanLogin
}

overheadOption = {
  "1": "find.inbox",
  "2": "find.outbox"
}

def main():
  global session
  global singInOptions
  global signIn
  global overheadOption

  if "tmp" not in os.listdir():
    os.mkdir("tmp")

  if "reports" not in os.listdir():
    os.mkdir("reports")

  h.checkLib() # Important when convert to exe

  print(banner)

  signInChoice = h.signInHandler()
  overheadChoice = h.overheadHandler()
  fromDate, toDate = h.dateHandler()
  # fromDate, toDate = "01-01-2024", "31-12-2024" # Debugging purpose

  requirements = singInOptions[signInChoice]()
  session = signIn[signInChoice](requirements, session)

  certificates = w.listCertificates(session)
  certificateChoice = h.certificateHandler(certificates)
  selectedCertificate = certificates[certificateChoice-1]

  session = w.getDashboard(selectedCertificate,session)

  today = time.localtime()
  filename = f"{today.tm_mday}-{today.tm_mon}-{today.tm_year}_{overheadOption[overheadChoice].split('.')[1]}_report_of_{fromDate}--{toDate}.csv"
  # filename = f"{today.tm_mday}-{today.tm_mon}-{today.tm_year}_inbox_report_of_{fromDate}--{toDate}.csv" # Debugging purpose

  headers = "Tarix, Göndərən tərəf, Göndərən VÖEN, Qəbul edən tərəf, Qəbul edən VÖEN, Mesaj, Serial kod, Status, Malın adı, Malın kodu, Barkod, Ölçü vahidi, Miqdarı / Həcmi, Vahidin satış qiyməti, Cəmi məbləği(manatla) 6*7, Aksiz dərəcəsi(%), Aksiz Məbləği(manatla), Cəmi 6*7+10, ƏDV-yə 18% cəlb edilən, ƏDV-yə 0% cəlb edilən, ƏDV-dən azad olunan, ƏDV-yə cəlb edilməyən, ƏDV məbləği (11*0.18), Yol vergisi, Yekun Məbləğ (11+16+17), URL\n"
  h.setCsvHeaders(filename, headers)
  URLS = w.getInvoiceUrls(overheadOption[overheadChoice], fromDate, toDate, session)
  w.getOverheads(URLS, session, filename)
  w.logout(session)
  h.convertToXlsx("./tmp/", filename)
  h.cleanTmp()
  h.fileOpenerHandler(filename)
  sys.exit()

try:
  os.system("cls")
  main()
except KeyboardInterrupt:
  print(f"\n{c.FG_RED}[!] Exiting Program! {c.END}")
  sys.exit()
  input()
except Exception as e:
  print(f"\n{c.FG_RED}[!] Some error happened! {c.END}")
  # print(e.with_traceback())
  input()

# main()