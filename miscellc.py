#!/usr/bin/env python3

# Program to parse miscell programs and generate CSV sheets.
# Dr Owain Kenway, 2016
# Distributed under the MIT license.

import string, sys
letters=list(string.ascii_uppercase)

# Convert number references to letter references.
def numtoletter(num):
  a=num%26
  if (a == num):
    return letters[num]
  else:
    return numtoletter(int(num/26)-1) + letters[a]

# And back
def lettertonum(letter):
  if len(letter) == 1:
    return letters.index(letter[0].upper())
  else:
    return letters.index(letter[len(letter)-1].upper()) + (26 * (lettertonum(letter[:-1])+1))

# Convert store to a list representation of the table.
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
    le = lettertonum(a.strip('0123456789'))
    table[le][n] = store[a]
  return table

# Output into CSV
def outputcsv(table, csvfile, sep, maxl, maxn):
  csv="" 
  for h in range(maxn+1):
    line = ""
    for d in range(maxl+1):
       line = line + table[d][h] + sep
    csv = csv + line + "\n"

  of = open(csvfile, 'w')
  of.write(csv)

# Code to get number out of a cell reference
def celltonum(address):
  return int(address.strip(string.ascii_uppercase).strip(string.ascii_lowercase))

# Code to get letter out of a cell reference
def celltoletter(address):
  return address.strip('0123456789')


# Code to import a CSV
def csvimport(offset, csvfile, sep):
  offnum = celltonum(offset)
  offlet = celltoletter(offset.upper())

  localstore = {}

  lslet = offlet

  f = open(csvfile, 'r')
  for line in f:
    lsnum = offnum
    items = line.split(sep=sep)

    for item in items:
      addr = lslet+str(lsnum)
      localstore[addr] = item.strip()
      lsnum = lsnum + 1

    lslet = numtoletter(lettertonum(lslet) + 1)

  f.close()

  return localstore
  
# Code to get the extent of a store
def getextent(store):
  maxl = 0
  maxn = 0

  for a in (store.keys()):
    anum = celltonum(a)
    alet = lettertonum(celltoletter(a))
    maxn=max(maxn,anum-1)
    maxl=max(maxl,alet)

  return [maxl, maxn] 

# Main parsing function
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
        elements = nocomments.strip().split()
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
      else: 
 
# If we've reached this stage, there is no rule for a line.
        print('ERROR - Unrecognisable line ' + str(lineno) + ': ' + line.strip())
        fail = fail + 1

# If we've failed to set address, don't do anything to data structures.
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

# Our main function.
if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser(description='Generate CSV from script.')
  parser.add_argument('-i', metavar='filename', type=str, help='Source file.')
  parser.add_argument('-o', metavar='filename', type=str, help='Output file.')
  parser.add_argument('-s', metavar='character', type=str, help='CSV seperator')

  args = parser.parse_args()
  
  of = 'out.csv'
  sep = '|'

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
    table = storetotable(store, maxl, maxn) 
    outputcsv(table, of, sep, maxl, maxn)

  else:
    print('Error - must specify input file.');
    sys.exit(2)
