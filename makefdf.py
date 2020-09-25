 #!/usr/bin/env python3
 
from fdfgen import forge_fdf
 
#fields = [('socio', 'John Smith'), ('telephone', '555-1234')]
fields = [('socio', 'John Smith')]  #, ('telephone', '555-1234')]

fdf = forge_fdf("",fields,[],[],[])
 
with open("test.fdf", "wb") as fdf_file:
     fdf_file.write(fdf)
