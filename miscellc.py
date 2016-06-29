#!/usr/bin/env python3

# First attempt at a parser.
# Operates on test.miscell.

import string
letters=list(string.ascii_uppercase)

# In memory representation of sheet.
store = {}

# Convert number references to letter references.
def numtoletter(num):
  a=num%26
  if (a == num):
    return letters[num]
  else:
    return numtoletter(int(num/26)-1) + letters[a]

def lettertonum(letter):
  if len(letter) == 1:
    return letters.index(letter[0].upper())
  else:
    return letters.index(letter[len(letter)-1].upper()) + (26 * (lettertonum(letter[:-1])+1))
     

def parse(filename, outfile, sep):
  f = open(filename, 'r')

# Max extent of sheet.
  maxn = 0
  maxl = 0

  for line in f:
    if (line[0] != '#') and (line.strip() != ''):
      pl = line.split(sep='<-')
      address = pl[0].strip()
      data = pl[1].strip()
      store[address] = data
      mynum = address.strip(string.ascii_uppercase).strip(string.ascii_lowercase)
      myletter = address.strip('0123456789')
      maxn=max(maxn,int(mynum)-1)
      maxl=max(maxl,lettertonum(myletter))
  f.close()

# Initialise in memory table
  c = []
  for i in range(maxl+1):    
    c.append([])
    for j in range(maxn+1):
      c[i].append('')

# Import store
  for a in store.keys():
    n = int(a.strip(string.ascii_uppercase).strip(string.ascii_lowercase))-1
    le = lettertonum(a.strip('0123456789'))
    c[le][n] = store[a]
 

# Output into CSV
  csv="" 
  for h in range(maxn+1):
    line = ""
    for d in range(maxl+1):
       line = line + c[d][h] + sep
    csv = csv + line + "\n"

  of = open(outfile, 'w')
  of.write(csv)

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
    parse(inf, of, sep)
  else:
    print('Error - must specify input file.');
