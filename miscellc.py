#!/usr/bin/env python3

# First attempt at a parser.

import string
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

# Main parsing function
def parse(filename):

# In memory representation of sheet.
  store = {}

# Max extent of sheet.
  maxn = 0
  maxl = 0

# Parse file
  f = open(filename, 'r')
  for line in f:
    if (line[0] != '#') and (line.strip() != ''):
      pl = line.split(sep='<-')
      address = pl[0].strip()
      data = '<-'.join(pl[1:]).strip()
      store[address] = data
      mynum = address.strip(string.ascii_uppercase).strip(string.ascii_lowercase)
      myletter = address.strip('0123456789')
      maxn=max(maxn,int(mynum)-1)
      maxl=max(maxl,lettertonum(myletter))
  f.close()

  return[store, maxl, maxn]


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
