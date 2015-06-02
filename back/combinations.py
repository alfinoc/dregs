import math

# Returns a cached version of given 'fn'.
def cached(fn):
   cache = {}
   def checkCache(*args):
      if args in cache:
         return cache[args]
      else:
         res = fn(*args)
         cache[args] = res
         return res
   return checkCache

# Returns (n choose k).
def choose(n, k):
   f = math.factorial
   if n < k:
      return 0
   return f(n) / f(k) / f(n-k)

# Returns maximum value c_k such that (c_k choose k) is less than or equal
# to 'remaining'.
def max_ck(k, remaining):
   n = k
   while choose(n, k) <= remaining:
      n += 1
   return n - 1

# Returns the k-combination corresponding to index i, using the combinatorial
# number system (see wiki) as a bijection from the natural numbers N to
# k-combinations of N.
def combination(k, i):
   sub = set()
   while k > 0:
      c_k = max_ck(k, i)
      i -= choose(c_k, k)
      k -= 1
      sub.add(c_k)
   return sub

# Returns the bitstring representation of s: the ith bit of the resulting
# integer is 1 iff i is in s.
def toBitString(s):
   res = 0
   for elt in s:
      res += 1 << elt
   return res

# Returns the subset of list 'pool' of given size with given combinatorial 'index'.
# Assumes no upper bound on index >= 0. Caps 'size' to number of elements in 'pool'.
def subset(pool, size, index):
   size = min(len(pool), size)
   chosen = combination(size, index % choose(len(pool), size))
   return map(lambda i : pool[i], chosen)

choose = cached(choose)
max_ck = cached(max_ck)
combination = cached(combination)
