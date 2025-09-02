def computeLPS(pat, M, lps):
  len = 0
  i = 1
  lps[0] = 0
  while i < M:
    if pat[i] == pat[len]:
      lps[i] = len+1
      len+=1
      i+=1
    else:
      if len != 0:
        len = lps[len-1]
      else:
        lps[i] = 0
        i += 1

def KMP(pat, s):
  M = len(pat)
  N = len(s)
  lps = [0]*M
  computeLPS(pat, M, lps)

  i = 0 # string ptr
  j = 0 # pat ptr
  while i < N:
    if  pat[j] == s[i]:
      i+=1
      j+=1
    else:
      if j != 0:
        j = lps[j-1]
      else:
        i += 1

    if j == M:
      print(i-j)
      j = lps[j-1]


string = "Robbery and Homicide"
pattern =  "and"

KMP(pattern, string)