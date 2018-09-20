#!/usr/bin/env python3

"""

   Copyright 2018 Evangelos I. Sarmas

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""

"""

 /*
  * @(#) E.Sarmas   philox.py 1.0 (2018-07-28)
  *
  * Author: E.Sarmas
  *
  * Created: 2018-07-28
  *
  * Description: philox random number generation implementation
  *
  * Version: 1.0
  * Version-Date: 2018-07-28
  *
  * Version-Log:
  *   1.0   (2018-07-28)   first implementation, full counter returned, used is repsonsible for initial counter and key
  */

"""

VERSION_STR = "philox   1.0 (2018-07-28)"



"""

cases:
  philox2 2 numbers at a time (counter:2, key:1)
  philox4 4 numbers at a time (counter:4, key:2)
  and # rounds = 1..16 (default 10)
  W = word size, 32 or 64

  mulhi(a, b) = trunc((a × b) / 2^W)
  mullo(a, b) = (a × b) mod 2^W
  
  L' = mullo(R, M)
  R' = mulhi(R, M) ^ k ^ L
  
  result counter is assumed big-endian
  
"""

# 64 bit
PHILOX_M2_64_0 = 0xD2B74407B1CE6E93
PHILOX_M2_64 = [0xD2B74407B1CE6E93]

PHILOX_M4_64_0 = 0xD2E7470EE14C6C93
PHILOX_M4_64_1 = 0xCA5A826395121157
PHILOX_M4_64 = [0xD2E7470EE14C6C93, 0xCA5A826395121157]

# 32 bit
PHILOX_M2_32_0 = 0xD256D193
PHILOX_M2_32 = [0xD256D193]

PHILOX_M4_32_0 = 0xD2511F53
PHILOX_M4_32_1 = 0xCD9E8D57
PHILOX_M4_32 = [0xD2511F53, 0xCD9E8D57]

# 64 bit
PHILOX_W_64_0 = 0x9E3779B97F4A7C15   # golden ratio
PHILOX_W_64_1 = 0xBB67AE8584CAA73B   # sqrt(3)-1
PHILOX_W_64 = [0x9E3779B97F4A7C15, 0xBB67AE8584CAA73B]

# 32 bit
PHILOX_W_32_0 = 0x9E3779B9   # golden ratio
PHILOX_W_32_1 = 0xBB67AE85   # sqrt(3)-1
PHILOX_W_32 = [0x9E3779B9, 0xBB67AE85]

# counter and key will be lists indexed by predefined names
# instead of classes with __slots__ or namedtuples, for performance

# names for indexes
VAL_1 = 0
VAL_2 = 1
VAL_3 = 2
VAL_4 = 3

MASK_64 = 0xffffffffffffffff
MASK_32 = 0xffffffff



###############################################################
#
#  Philox
#
###############################################################

# each philox x2 or x4 calls base philox with specific
# _round(), _bumpkey() functions and word length, mask parameters
def philox2_32(counter, key, rounds=10):
  return philox(counter, key, philox2_round, PHILOX_M2_32, philox2_bumpkey, PHILOX_W_32, 32, MASK_32, rounds)

def philox2_64(counter, key, rounds=10):
  return philox(counter, key, philox2_round, PHILOX_M2_64, philox2_bumpkey, PHILOX_W_64, 64, MASK_64, rounds)

def philox4_32(counter, key, rounds=10):
  return philox(counter, key, philox4_round, PHILOX_M4_32, philox4_bumpkey, PHILOX_W_32, 32, MASK_32, rounds)
  
def philox4_64(counter, key, rounds=10):
  return philox(counter, key, philox4_round, PHILOX_M4_64, philox4_bumpkey, PHILOX_W_64, 64, MASK_64, rounds)

# not called but inlined
def philox_mulihilo(a, b, len_w, mask_w):
  prod = a * b
  return prod >> len_w, prod & mask_w

# _round() in 2 versions for x2 or x4
def philox2_round(counter, key, philox_m, len_w, mask_w):
  # philox_mulhilo
  prod = philox_m[VAL_1] * counter[VAL_1]
  hi_2 = prod >> len_w
  lo_2 = prod & mask_w
  counter[VAL_1] = hi_2 ^ counter[VAL_2] ^ key[VAL_1]
  counter[VAL_2] = lo_2

def philox4_round(counter, key, philox_m, len_w, mask_w):
  prod = philox_m[VAL_1] * counter[VAL_1]
  hi_1 = prod >> len_w
  lo_1 = prod & mask_w
  prod = philox_m[VAL_2] * counter[VAL_3]
  hi_2 = prod >> len_w
  lo_2 = prod & mask_w
  counter[VAL_1] = hi_2 ^ counter[VAL_2] ^ key[VAL_1]
  counter[VAL_2] = lo_2
  counter[VAL_3] = hi_1 ^ counter[VAL_4] ^ key[VAL_2]
  counter[VAL_4] = lo_1

# _bumpkey() in 2 versions for x2 or x4
def philox2_bumpkey(key, philox_w, len_w, mask_w):
  key[VAL_1] = (key[VAL_1] + philox_w[VAL_1]) & mask_w

def philox4_bumpkey(key, philox_w, len_w, mask_w):
  key[VAL_1] = (key[VAL_1] + philox_w[VAL_1]) & mask_w
  key[VAL_2] = (key[VAL_2] + philox_w[VAL_2]) & mask_w

# philox_round = _round() function specific for x2 or x4
# philox_bumpkey = _bumpkey() function specific for x2 or x4
# mask_w = mask all 1(s) for 32 or 64 bits
# rounds = 1..16, default = 10
def philox(counter, key, philox_round, philox_m, philox_bumpkey, philox_w, len_w, mask_w, rounds = 10):
  for i in range(rounds - 1):
    philox_round(counter, key, philox_m, len_w, mask_w) # updates counter
    philox_bumpkey(key, philox_w, len_w, mask_w) # updates key
  philox_round(counter, key, philox_m, len_w, mask_w) # updates counter
  return counter



#
# main function that returns random() float in range [0.0, 1.0), uses philox2_64-7 internally
# there can be other functions too making special use of the "state" of the generator
# for example, to always produce random 32 bit integers (splitting the 64 bit integers in two)
# or provide for parallel generation
# and using other philox parameters and initialization methods
#
# these functions should be the only accessible functions by applications
# usage:
#   plilox.seed(a=None)
#   philox.random()
#

counter = [0x243f6a8885a308d3, 0x13198a2e03707344]
key = [0xa4093822299f31d0]
p = [1]

def seed(a):
  key[0] = a

def random():
  if p[0] == 1:
    # assumes increasing 1st part is enough
    counter[0] += 1
    philox2_64(counter, key, rounds=7)
    p[0] = 0
    return counter[1] / MASK_64
  else:
    p[0] = 1
    return counter[0] / MASK_64



#
# unit test
#

# test cases with results, single line form
# copied verbatim from original source (in comment) and
# used to drive tests
TEST_CASES = """
#nameNxW  R  CTR                                 KEY                                   EXPECTED
#
philox2x32 7 00000000 00000000 00000000   257a3673 cd26be2a
philox2x32 7 ffffffff ffffffff ffffffff   ab302c4d 3dc9d239
philox2x32 7 243f6a88 85a308d3 13198a2e   bedbbe6b e4c770b3
philox2x32 10 00000000 00000000 00000000   ff1dae59 6cd10df2
philox2x32 10 ffffffff ffffffff ffffffff   2c3f628b ab4fd7ad
philox2x32 10 243f6a88 85a308d3 13198a2e   dd7ce038 f62a4c12
#
philox2x64 7 0000000000000000 0000000000000000 0000000000000000   b41da69fbfefc666 511e9ce1a5534056
philox2x64 7 ffffffffffffffff ffffffffffffffff ffffffffffffffff   a4696cc04462015d 724782dae17169e9
philox2x64 7 243f6a8885a308d3 13198a2e03707344 a4093822299f31d0   98ed1534392bf372 67528b1568882fd5
philox2x64 10 0000000000000000 0000000000000000 0000000000000000   ca00a0459843d731 66c24222c9a845b5
philox2x64 10 ffffffffffffffff ffffffffffffffff ffffffffffffffff   65b021d60cd8310f 4d02f3222f86df20
philox2x64 10 243f6a8885a308d3 13198a2e03707344 a4093822299f31d0   0a5e742c2997341c b0f883d38000de5d
#
philox4x32 7 00000000 00000000 00000000 00000000 00000000 00000000   5f6fb709 0d893f64 4f121f81 4f730a48
philox4x32 7 ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff   5207ddc2 45165e59 4d8ee751 8c52f662
philox4x32 7 243f6a88 85a308d3 13198a2e 03707344 a4093822 299f31d0   4dfccaba 190a87f0 c47362ba b6b5242a
philox4x32 10 00000000 00000000 00000000 00000000 00000000 00000000   6627e8d5 e169c58d bc57ac4c 9b00dbd8
philox4x32 10 ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff   408f276d 41c83b0e a20bc7c6 6d5451fd
philox4x32 10 243f6a88 85a308d3 13198a2e 03707344 a4093822 299f31d0   d16cfe09 94fdcceb 5001e420 24126ea1
#
philox4x64 7 0000000000000000 0000000000000000 0000000000000000 0000000000000000 0000000000000000 0000000000000000   5dc8ee6268ec62cd 139bc570b6c125a0 84d6deb4fb65f49e aff7583376d378c2
philox4x64 7 ffffffffffffffff ffffffffffffffff ffffffffffffffff ffffffffffffffff ffffffffffffffff ffffffffffffffff   071dd84367903154 48e2bbdc722b37d1 6afa9890bb89f76c 9194c8d8ada56ac7
philox4x64 7 243f6a8885a308d3 13198a2e03707344 a4093822299f31d0 082efa98ec4e6c89 452821e638d01377 be5466cf34e90c6c   513a366704edf755 f05d9924c07044d3 bef2cb9cbea74c6c 8db948de4caa1f8a
philox4x64 10 0000000000000000 0000000000000000 0000000000000000 0000000000000000 0000000000000000 0000000000000000   16554d9eca36314c db20fe9d672d0fdc d7e772cee186176b 7e68b68aec7ba23b
philox4x64 10 ffffffffffffffff ffffffffffffffff ffffffffffffffff ffffffffffffffff ffffffffffffffff ffffffffffffffff   87b092c3013fe90b 438c3c67be8d0224 9cc7d7c69cd777b6 a09caebf594f0ba0
philox4x64 10 243f6a8885a308d3 13198a2e03707344 a4093822299f31d0 082efa98ec4e6c89 452821e638d01377 be5466cf34e90c6c   a528f45403e61d95 38c72dbd566e9788 a5a1610e72fd18b5 57bd43b5e52b7fe6
"""

import unittest

class Test_philox(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    pass
  
  @classmethod
  def tearDownClass(cls):
    pass
  
  def setUp(self):
    pass
  
  def tearDown(self):
    pass
  
  def test_run(self):
    for line in TEST_CASES.split("\n"):
      if line and line[0] != "#":
        test_desc = line.split()
        test_desc = [test_desc[0], int(test_desc[1])] + [int(x, 16) for x in test_desc[2:]]
        print(test_desc)
        if test_desc[0] == "philox2x32":
          test_func = philox2_32
          rounds = test_desc[1]
          counter = [test_desc[2], test_desc[3]]
          key = [test_desc[4]]
          res = [test_desc[5], test_desc[6]]
        elif test_desc[0] == "philox2x64":
          test_func = philox2_64
          rounds = test_desc[1]
          counter = [test_desc[2], test_desc[3]]
          key = [test_desc[4]]
          res = [test_desc[5], test_desc[6]]
        elif test_desc[0] == "philox4x32":
          test_func = philox4_32
          rounds = test_desc[1]
          counter = [test_desc[2], test_desc[3], test_desc[4], test_desc[5]]
          key = [test_desc[6], test_desc[7]]
          res = [test_desc[8], test_desc[9], test_desc[10], test_desc[11]]
        elif test_desc[0] == "philox4x64":
          test_func = philox4_64
          rounds = test_desc[1]
          counter = [test_desc[2], test_desc[3], test_desc[4], test_desc[5]]
          key = [test_desc[6], test_desc[7]]
          res = [test_desc[8], test_desc[9], test_desc[10], test_desc[11]]
        #
        run_res = test_func(counter, key, rounds)
        #self.assertEqual()
        self.assertTrue(run_res == res, msg="{}, result: {} (expected: {})".format(test_desc, run_res, res))



#
# microbenchmark
#

# philox pure python implementation runs ~ 2.5 times slower than native random number generator
#
# for reference
# i3-5005U, Windows 10 Home, Python 3.6 => ~ 0.16 Mop/s philox2_64-7 random(), 0.40 Mop/s python random

import time
import timeit
import random as p_random

def benchmark():
  # CONSTANTS
  M1 = 1000000 # 1 million
  # adjustable values
  NUMBERS = 500000
  REPEAT = 2
  
  # philox2_32 => 2x4 bytes = 8 bytes per call
  BYTES_CALL = 8
  #philox2x32 10 243f6a88 85a308d3 13198a2e   dd7ce038 f62a4c12
  philox2_32_b = "philox2_32([0x243f6a88, 0x85a308d3], [0x13198a2e])"
  t = min(timeit.repeat(philox2_32_b, repeat=REPEAT, number=NUMBERS, globals=globals()))
  MOPs = (NUMBERS / M1) / t
  MBs = MOPs * BYTES_CALL
  print("philox2_32 MOPs = {:.3f}, MB/s = {:.3f}".format(MOPs, MBs))
  
  # philox2_64 => 2x8 bytes = 16 bytes per call
  BYTES_CALL = 16
  #philox2x64 10 243f6a8885a308d3 13198a2e03707344 a4093822299f31d0   0a5e742c2997341c b0f883d380
  philox2_64_b = "philox2_64([0x243f6a8885a308d3, 0x13198a2e03707344], [0xa4093822299f31d0])"
  t = min(timeit.repeat(philox2_64_b, repeat=REPEAT, number=NUMBERS, globals=globals()))
  MOPs = (NUMBERS / M1) / t
  MBs = MOPs * BYTES_CALL
  print("philox2_64 MOPs = {:.3f}, MB/s = {:.3f}".format(MOPs, MBs))
  
  # philox4_32 => 4x4 bytes = 16 bytes per call
  BYTES_CALL = 16
  #philox4x32 10 243f6a88 85a308d3 13198a2e 03707344 a4093822 299f31d0   d16cfe09 94fdcceb 5001e420 24126ea1
  philox4_32_b = "philox4_32([0x243f6a88, 0x85a308d3, 0x13198a2e, 0x03707344], [0xa4093822, 0x299f31d0])"
  t = min(timeit.repeat(philox4_32_b, repeat=REPEAT, number=NUMBERS, globals=globals()))
  MOPs = (NUMBERS / M1) / t
  MBs = MOPs * BYTES_CALL
  print("philox4_32 MOPs = {:.3f}, MB/s = {:.3f}".format(MOPs, MBs))
  
  # philox4_64 => 4x8 bytes = 32 bytes per call
  BYTES_CALL = 32
  #philox4x64 10 243f6a8885a308d3 13198a2e03707344 a4093822299f31d0 082efa98ec4e6c89 452821e638d01377 be5466cf34e90c6c   a528f45403e61d95 38c72dbd566e9788 a5a1610e72fd18b5 57bd43b5e52b7fe6
  philox4_64_b = "philox4_64([0x243f6a8885a308d3, 0x13198a2e03707344, 0xa4093822299f31d0, 0x082efa98ec4e6c89], [0x452821e638d01377, 0xbe5466cf34e90c6c])"
  t = min(timeit.repeat(philox4_64_b, repeat=REPEAT, number=NUMBERS, globals=globals()))
  MOPs = (NUMBERS / M1) / t
  MBs = MOPs * BYTES_CALL
  print("philox4_64 MOPs = {:.3f}, MB/s = {:.3f}".format(MOPs, MBs))
  
  # random_32 => 4 bytes per call
  BYTES_CALL = 4
  random_32_b = "p_random.randint(0, MASK_32)"
  t = min(timeit.repeat(random_32_b, repeat=REPEAT, number=NUMBERS, globals=globals()))
  MOPs = (NUMBERS / M1) / t
  MBs = MOPs * BYTES_CALL
  print("random_32 MOPs = {:.3f}, MB/s = {:.3f}".format(MOPs, MBs))
  
  # random_64 => 8 bytes per call
  BYTES_CALL = 8
  random_64_b = "p_random.randint(0, MASK_64)"
  t = min(timeit.repeat(random_64_b, repeat=REPEAT, number=NUMBERS, globals=globals()))
  MOPs = (NUMBERS / M1) / t
  MBs = MOPs * BYTES_CALL
  print("random_64 MOPs = {:.3f}, MB/s = {:.3f}".format(MOPs, MBs))
  
  # custom bench timing, to compare with timeit
  perf_time = time.perf_counter
  # philox2_32 => 2x4 bytes = 8 bytes per call
  BYTES_CALL = 8
  #philox2x32 10 243f6a88 85a308d3 13198a2e   dd7ce038 f62a4c12
  philox2_32_b = "philox2_32([0x243f6a88, 0x85a308d3], [0x13198a2e])"
  start = perf_time()
  for i in range(NUMBERS):
    philox2_32([0x243f6a88, 0x85a308d3], [0x13198a2e])
  stop = perf_time()
  t = stop - start
  MOPs = (NUMBERS / M1) / t
  MBs = MOPs * BYTES_CALL
  print("philox2_32 (custom timing) MOPs = {:.3f}, MB/s = {:.3f}".format(MOPs, MBs))
  
  # random()
  #philox2x64 7 243f6a8885a308d3 13198a2e03707344 a4093822299f31d0   98ed1534392bf372 67528b1568882fd5
  philox2_64_b = "philox2_64([0x243f6a8885a308d3, 0x13198a2e03707344], [0xa4093822299f31d0])"
  t = min(timeit.repeat("random()", repeat=REPEAT, number=NUMBERS, globals=globals()))
  MOPs = (NUMBERS / M1) / t
  print("random() MOPs = {:.3f}".format(MOPs))

def main():
  unittest.TestLoader.sortTestMethodsUsing = None
  test_suite = unittest.TestSuite()
  test_loader = unittest.TestLoader()
  test_suite.addTest(test_loader.loadTestsFromTestCase(Test_philox))
  test_runner = unittest.TextTestRunner(failfast=True)
  test_runner.run(test_suite)
  benchmark()

if __name__ == "__main__":
  main()