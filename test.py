import requests

dblp = 'http://dblp.org/search/publ/api?q='

title = 'Domain-Adversarial Training of Neural Networks'
title = '$+'.join(title.split(' '))
print(title)
res = requests.get(dblp + title)
print(res.text)