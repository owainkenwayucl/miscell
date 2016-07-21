#!/usr/bin/env python3

import miscellc


def test(result, expected, name, testc):
  if result != expected:
    testc[1] = testc[1] + 1
    print('Test "' + name + '" failed:')
    print('  Expected: ' + str(expected))
    print('  Got:      ' + str(result))
  else: 
    testc[0] = testc[0] + 1

if __name__ == '__main__':
  results = [0,0]

# Tests of validadd
  test(miscellc.validadd('A2'), True, "validadd('A2')", results)
  test(miscellc.validadd('spider'), False, "validadd('spider')", results)

# Finished
  print('Ran ' + str(results[0] + results[1]) + ' tests of which:')
  print('  ' + str(results[0]) + ' succeeded.')
  print('  ' + str(results[1]) + ' failed.')

