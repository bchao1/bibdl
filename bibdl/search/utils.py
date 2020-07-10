

def normalize(s):
    s = ''.join(c for c in s if c.isalpha())
    return ''.join(list(map(str.strip, s.strip().split(' ')))).lower()
