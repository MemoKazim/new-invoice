import re

def validateDate(date):
  dateRegex = r"^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-(\d{4})$"
  return re.match(dateRegex, date)

def validatePhone(phone):
  phoneRegex = r"^\+994\d{9}$"
  return re.match(phoneRegex, phone)

def validateID(id):
  idRegex = r"^\d{6}$"
  return re.match(idRegex, id)
