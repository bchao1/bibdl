
def normalize(s):
    return ''.join(list(map(str.strip, s.strip().split(' ')))).lower()