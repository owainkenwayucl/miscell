#!/usr/bin/env python3

# Program to parse miscell programs and generate CSV sheets.
# Dr Owain Kenway, 2016
# Distributed under the MIT license.

import string, sys, shlex
letters=list(string.ascii_uppercase)
numbers='0123456789'

# -----------------------------------------------
# Convert number references to letter references.
# -----------------------------------------------
def numtoletter(num):
  a=num%26
  if (a == num):
    return letters[num]
  else:
    return numtoletter(int(num/26)-1) + letters[a]

# ---------
# And back.
# ---------
def lettertonum(letter):
  if len(letter) == 1:
    return letters.index(letter[0].upper())
  else:
    return letters.index(letter[len(letter)-1].upper()) + (26 * (lettertonum(letter[:-1])+1))

# -------------------------
# Validate address strings.
# -------------------------
def validadd(addr):
  upaddr=addr.upper().strip()
  left=''
  right=''
  stop=False
# split at first nonletter
  for a in upaddr:
    if a in letters and not stop:
      left = left + a
    else:
      stop = True
      right = right + a
  
  isLetter=(len(left) > 0)
    
  
  isNumber=True
  for b in right:
    if b not in numbers:
      isNumber=False
  if len(right)==0:
    isNumber=False

  return (isLetter and isNumber)
  
# ----------------------------------------------------
# Convert store to a list representation of the table.
# ----------------------------------------------------
def storetotable(store, maxl, maxn):

# Initialise in memory table
  table = []
  for i in range(maxl+1):    
    table.append([])
    for j in range(maxn+1):
      table[i].append('')

# Import store
  for a in store.keys():
    n = int(a.strip(string.ascii_uppercase).strip(string.ascii_lowercase))-1
    le = lettertonum(a.strip(numbers))
    table[le][n] = store[a]
  return table

# ----------------
# Output into CSV.
# ----------------
def outputcsv(table, csvfile, sep, maxl, maxn):
  csv="" 
  for h in range(maxn+1):
    line = ""
    for d in range(maxl+1):
       line = line + table[d][h] + sep
    csv = csv + line + "\n"

  of = open(csvfile, 'w')
  of.write(csv)
  of.close()

# -------------------------------------------
# Code to get number out of a cell reference.
# -------------------------------------------
def celltonum(address):
  return int(address.strip(string.ascii_uppercase).strip(string.ascii_lowercase))

# -------------------------------------------
# Code to get letter out of a cell reference.
# -------------------------------------------
def celltoletter(address):
  return address.strip('0123456789')

# ---------------------
# Code to import a CSV.
# ---------------------
def csvimport(offset, csvfile, sep):
  offnum = celltonum(offset)
  offlet = celltoletter(offset.upper())
  localstore = {}
  lsnum = offnum

  f = open(csvfile, 'r')

  for line in f:
    lslet = offlet
    items = line.split(sep=sep)

    for item in items:
      addr = lslet+str(lsnum)
      localstore[addr] = item.strip()
      lslet = numtoletter(lettertonum(lslet) + 1)

    lsnum = lsnum + 1

  f.close()
  return localstore

# ----------------------------------  
# Code to get the extent of a store.
# ----------------------------------
def getextent(store):
  maxl = 0
  maxn = 0

  for a in (store.keys()):
    anum = celltonum(a)
    alet = lettertonum(celltoletter(a))
    maxn=max(maxn,anum-1)
    maxl=max(maxl,alet)

  return [maxl, maxn] 

# ----------------------------------------
# Code to dump a store out to an mcl file.
# ----------------------------------------
def dumpmcl(store, outputfile):
  addresses = list(store.keys())
  addresses.sort()

  mcl = '# Auto generated MCL file.\n'
  for item in addresses:
# If we have a right assignment and a <- in the data segment we should do a
# right assignment in the dumped mcl to avoid generating ambiguous lines.
    if store[item].strip() != "":
      if '->' in store[item]:
        mcl = mcl + store[item] + ' -> ' + item + '\n'
      else:
        mcl = mcl + item + ' <- ' + store[item] + '\n'

  f = open(outputfile, 'w')
  f.write(mcl)
  f.close()      

# ---------------------------------------------
# Code to navigate a JSON path in a dictionary.
# ---------------------------------------------

def navj(jdict, path):
  if (len(path) == 0):
    return jdict
  else:
    return(navj(jdict[path[0]], path[1:]))

# --------------------
# Code to import JSON.
# --------------------
def jsonimport(offset, jsonfile, jsonpath, jsonfield):
  import json
 
  splitpath = jsonpath.split()

# Import json file
  f = open(jsonfile, 'r')
  jdict = json.load(f)

# Navigate to right place in file dict
  jstor = navj(jdict, splitpath)

  if (type(jstor) is list):
    return implist(offset, jstor, jsonfield.split())
  else:
    return impdict(offset, jstor, jsonfield.split())

# -------------------
# Code to import dict
# -------------------
def impdict(offset, d, fields):
  localstore = {}

# What we have here is a dictionary and a set of keys to add.

  offnum = celltonum(offset)
  offlet = celltoletter(offset.upper())

# Generate column headers.
  lsnum = offnum
  lslet = offlet
  for c in fields:
    addr = lslet+str(lsnum)
    localstore[addr] = str(c).strip()
    lslet = numtoletter(lettertonum(lslet) + 1)

# Generate columns.
  lsnum = offnum + 1
  lslet = offlet
  for e in fields:
    addr = lslet+str(lsnum)
    localstore[addr] = str(d[e]).strip()
    lslet = numtoletter(lettertonum(lslet) + 1)

  return localstore


# --------------------
# Code to import list.
# --------------------
def implist(offset, l, fields):
  localstore = {}

# OK, what we hope to have at this point is a list of dicts, each of which are
# key paired to some of the values in fields.
  offnum = celltonum(offset)
  offlet = celltoletter(offset.upper())

  lsnum = offnum
  lslet = offlet

# Generate column headers.
  for c in fields:
    addr = lslet+str(lsnum)
    localstore[addr] = str(c).strip()

    lslet = numtoletter(lettertonum(lslet) + 1)
    
# Generate columns.
  lsnum = offnum + 1
  
  for a in l:
    lslet = offlet
    for b in fields:
      addr = lslet+str(lsnum)
      localstore[addr] = str(a[b]).strip()

      lslet = numtoletter(lettertonum(lslet) + 1)
    lsnum = lsnum + 1

  return localstore


# ----------------------
# Main parsing function.
# ----------------------
def parse(filename):

# In memory representation of sheet.
  store = {}

# Max extent of sheet.
  maxn = 0
  maxl = 0

# Parse file
  f = open(filename, 'r')
  lineno = 1
  fail = 0
  warnings = 0
  for line in f:

# Knock out everything to the right of a comment.
    nocomments = line.split(sep="#")[0].strip() 
    address = 'UNSET'
# Ignore blank/entirely comment lines
    if nocomments != '':
      if '<-' in nocomments:

# Catch ambiguous lines.
        if '->' in nocomments:
          print('ERROR - Ambiguous line ' + str(lineno) + ': ' + line.strip())
          print('  (this error is caused by having both a <- and a -> on one line)')
          fail = fail + 1 
        else:
          pl = nocomments.split(sep='<-')
          address = pl[0].strip().upper()
          data = '<-'.join(pl[1:]).strip()
      elif '->' in nocomments:
        pl = nocomments.split(sep='->')
        address = pl[len(pl)-1].strip().upper()
        data = '->'.join(pl[len(pl)-1:]).strip()
      elif nocomments.strip().split()[0].lower() == 'data:':
        elements = shlex.split(nocomments.strip())
        if len(elements) != 4:
          print('ERROR - Wrong number of elements on data line ' + str(lineno) + ': ' + line.strip())
          print('  Data line should be of the format data: <cell> <file> <separator>')
          fail = fail + 1
        else:
          datastore = csvimport(elements[1], elements[2], elements[3])
          for item in datastore.keys():
            if item in store.keys():
              print('WARNING - Overwriting element: ' + item)
              print('  Original value: ' + store[item])
              print('  New value: ' + datastore[item])
              warnings = warnings + 1
            store[item] = str(datastore[item])
          ext = getextent(store)
          maxl = ext[0]
          maxn = ext[1]
      elif nocomments.strip().split()[0].lower() == 'json:':
        elements = shlex.split(nocomments.strip())
        if len(elements) != 5:
          print('ERROR - Wrong number of elements on JSON line ' + str(lineno) + ': ' + line.strip())
          print('  JSON line should be of the format json: <cell> <file> <path> <fields>')
          fail = fail + 1
        else:
          datastore = jsonimport(elements[1], elements[2], elements[3], elements[4])
          for item in datastore.keys():
            if item in store.keys():
              print('WARNING - Overwriting element: ' + item)
              print('  Original value: ' + store[item])
              print('  New value: ' + datastore[item])
              warnings = warnings + 1
            store[item] = str(datastore[item])
          ext = getextent(store)
          maxl = ext[0]
          maxn = ext[1]
      elif nocomments.strip().split()[0].lower() == 'fillcol:':
        elements = shlex.split(nocomments.strip())
        if len(elements) != 5:
          print('ERROR - Wrong number of elements on fill column line ' + str(lineno) + ': ' + line.strip())
          print('  Fill column line should be of the format fillcol: <letter> <start> <finish> <data>')
          fail = fail + 1
        else:
          fillcolletter = elements[1]
          fillcolstart = int(elements[2])
          fillcolstop = int(elements[3])
          fillcoldat = elements[4]
          for colcel in range(fillcolstart, fillcolstop+1):
            colladdr = fillcolletter.upper() + str(colcel)
            if colladdr in store.keys():
              print('WARNING - Overwriting element: ' + item)
              print('  Original value: ' + store[item])
              print('  New value: ' + datastore[item])
              warnings = warnings + 1
            store[colladdr] = fillcoldat
          ext = getextent(store)
          maxl = ext[0]
          maxn = ext[1]
      elif nocomments.strip().split()[0].lower() == 'fillrow:':
        elements = shlex.split(nocomments.strip())
        if len(elements) != 5:
          print('ERROR - Wrong number of elements on fill row line ' + str(lineno) + ': ' + line.strip())
          print('  Fill column line should be of the format fillrow: <number> <start> <finish> <data>')
          fail = fail + 1
        else:
          fillrownum = int(elements[1])
          fillrowstart = lettertonum(elements[2])
          fillrowstop = lettertonum(elements[3])
          fillrowdat = elements[4]
          for rowcel in range(fillrowstart, fillrowstop+1):
            rowaddr = numtoletter(rowcel) + str(fillrownum)
            if rowaddr in store.keys():
              print('WARNING - Overwriting element: ' + item)
              print('  Original value: ' + store[item])
              print('  New value: ' + datastore[item])
              warnings = warnings + 1
            store[rowaddr] = fillrowdat
          ext = getextent(store)
          maxl = ext[0]
          maxn = ext[1]
      else: 
 
# If we've reached this stage, there is no rule for a line.
        print('ERROR - Unrecognisable line ' + str(lineno) + ': ' + line.strip())
        fail = fail + 1

# If we've failed to set address, don't do anything to data structures.
      if not validadd(address) and address != 'UNSET':
        print('ERROR - Invalid cell address on line ' + str(lineno) + ': ' + str(address))
        fail = fail + 1
        address = 'UNSET'
      if address != 'UNSET':
        if address in store.keys():
          print('WARNING - Overwriting element: ' + address)
          print('  Original value: ' + store[address])
          print('  New value: ' + data)
          warnings = warnings + 1
        store[address] = data
        mynum = celltonum(address)
        myletter = celltoletter(address)
        maxn=max(maxn,mynum-1)
        maxl=max(maxl,lettertonum(myletter))
    lineno = lineno + 1
  f.close()

# If we had warnings, report.
  if warnings > 0:
    print(str(warnings) + ' warnings while processing "' + filename + '".')

# If fail has been set while parsing, exit with a 1.
  if fail > 0:
    print(str(fail) + ' errors in file "' + filename + '", exiting without proceeding...')
    sys.exit(1)

  return[store, maxl, maxn]

# ------------------
# Our main function.
# ------------------
if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser(description='Generate CSV from script.')
  parser.add_argument('-i', metavar='filename', type=str, help='Source file.')
  parser.add_argument('-o', metavar='filename', type=str, help='Output file.')
  parser.add_argument('-s', metavar='character', type=str, help='CSV seperator.')
  parser.add_argument('-d', metavar='filename', type=str, help='Dump intermediate MCL to file.')
  parser.add_argument('-b', action='store_true', help='Convert CSV to MCL.')

  args = parser.parse_args()
  sep = '|'
  
  if args.b:
# backwards operaton (CSV -> MCL).
    of = 'out.mcl'

    if (args.i != None):
      inf = args.i
      if (args.o != None):
        of = args.o    
      if (args.s != None):
        sep = args.s
      store = csvimport('A1', inf, sep)
      if (args.d != None):
        dumpmcl(store, args.d)
      dumpmcl(store, of)
    else:
      print('Error - must specify input file.');
      sys.exit(2)
    
  else:
# normal operation (MCL -> CSV).
    of = 'out.csv'
    
    if (args.i != None):
      inf = args.i
      if (args.o != None):
        of = args.o
      if (args.s != None):
        sep = args.s
      p = parse(inf)
      store = p[0]
      maxl = p[1]
      maxn = p[2]
      if (args.d != None):
        dumpmcl(store, args.d)
      table = storetotable(store, maxl, maxn) 
      outputcsv(table, of, sep, maxl, maxn)

    else:
      print('Error - must specify input file.')
      sys.exit(2)
