#!/usr/bin/python3
# -*- coding: latin-1 -*-
# disclaimer:
# il codice è pessimo, venuto su un pezzettino alla volta senza uno schema predetermonato
# sicuramente da rifare meglio magari usando almeno la classe "certificato" ma...TODO
import os
import sys
import fileinput
import shutil
import csv
import psycopg2
from psycopg2 import extras
#from fdfgen import forge_fdf
import time
print('comincio')
try:
    connection = psycopg2.connect(user = "adempiere",
                                  password = "adempiere",
                                  host = "127.0.0.1",
                                  port = "5454",
                                  database = "idempiere")

    cursor = connection.cursor(cursor_factory=extras.DictCursor)
    # Print PostgreSQL Connection properties
    print ('i parametri della connessione--------\n', connection.get_dsn_parameters(),"\n")

    # Print PostgreSQL version
    query="select ROW_NUMBER() over (order by datefrom) as num, name ,description as des,lit_courses_id::varchar as id  from lit_courses ;"
    print(query)
    cursor.execute(query)
    corsi = cursor.fetchall()
    print(corsi)
    print('Di quale corso vuoi fare i certificati?' );
    
    for corso in corsi:
        
        
        #print(str(corso[0]).ljust(2),': ',corso[1].ljust(25),'\t\t',corso[2])
        print(str(corso['num']).ljust(2),': ',corso['name'].ljust(25),'\t\t',corso['des'])
        
    id=input('\033[1;33;40m(scrivi il numero corrispondente)->\033[1;37;40m')        

    corso_id=corsi[int(id)-1]['id']
    corso=   corsi[int(id)-1]['name'].replace(" ","_")
    print('hai scelto il corso:   ',corso)
    query="select cs.name,u.name nome,u.surname cognome,u.email as email  from ad_user u join fact_acct_simple c  on c.ad_user_id= u.ad_user_id join lit_courses cs on c.lit_courses_id = cs.lit_courses_id where cs.lit_courses_id = '"+ corso_id +"';"
    print(query)
    copy="copy ("+query+") to '/tmp/elenco.csv' DELIMITER ',' CSV HEADER;"
    print(copy)
    #query="select version()"
    #query=""
    cursor.execute(query)
    allievi = cursor.fetchall()


    print('ecco i corsisti: \n',allievi)
    
    
    for allievo in allievi:
        
        #print(allievo,'\n')
        print(allievo['nome'].rjust(20),allievo['cognome'].ljust(20),allievo['email'],)
        

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")




#select name description from lit_courses;
''' parto dal presupposto che il file odt originale abbia tre caselle di testo con nomi:
nome cognome classe
rispettivamente con testo predefinito
Mario Rossi CLASSE
Esporto come... Esporta nel formato pdf  
spuntare:
tag
crea formulario pdf
(formato invio dati FDF)
esporta
l'elenco dei nomi in un file .csv con colonne
nome,cognome,email 
(come minimo questi nomi esatti, non ha importanza l'ordine, se ce ne sono altri verranno ignorati
per ottenerlo uno dei mille modi è:
mi collego al db idempiere
psql -U adempiere idempiere
sul db di idempiere scarico la lista in csv dei corsisti
copy (select cs.name,u.name nome,u.surname cognome,u.email as email  from ad_user u join fact_acct_simple c  on c.ad_user_id= u.ad_user_id join lit_courses cs on c.lit_courses_id = cs.lit_courses_id where cs.name = 'Python da Zero 2019';) to '/tmp/Python2019.csv' DELIMITER ',' CSV HEADER;

''' 
# per far funzionare il tutto creo una cartella 
# e dentro ci metto il  
# pdf   CON LO STESSO NOME DELLA CARTELLA
# csv   CON LO STESSO NOME DELLA CARTELLA
# gli altri file se li crea lo script da solo

#corso=str(sys.argv[1])
print('creo i certificati per il corso: ',corso)
#exit()
# la cartella dove salverò i certificati
dir_c='certificati'
# elenco dei nomi per i certificati
#elenco=corso+'/'+corso+'.csv'
template_pdf=corso+'/'+corso+'.pdf'
template= corso+'/'+corso+'.fdf' 	# originale da non modificare

#fields = [('name', 'John Smith'), ('telephone', '555-1234')]
#fdf = forge_fdf("",fields,[],[],[])
# 
#with open("data.fdf", "wb") as fdf_file:
#     fdf_file.write(fdf)
#


cmd='pdftk '+ template_pdf + ' generate_fdf  output '+ template

# pdftk original.pdf generate_fdf output fillform.fdf  # lapalissiano
os.system(cmd)




dirName = corso+'/'+dir_c
 
try:
    # Create target Directory
    os.mkdir(dirName)
    print("Directory " , dirName ,  " Created ") 
except FileExistsError:
    print("Directory " , dirName ,  " already exists")
# non so perchè ma devo cancellare la seconda riga perchè manda in vacca tutto
    
cmd="sed -i '2d' "+ template
os.system(cmd)
#os.system('cat '+ template)

orig_words=('socio')
# nome del file che userò come stampino modificabile
stamp= corso+'Stamp.fdf'		 	# la copia da modificare

#corsisti = csv.DictReader(open(elenco))
corsisti=allievi
# adesso per ogni corsista 
for d in corsisti:
  # per evitare casini rimpiazzo i caratteri sporcaccioni
  nome=d['nome'].rstrip()  #.replace("'","_").replace(" ","_")
  cognome=d['cognome'].replace("'","_").replace(" ","_")  # sostituisco l'apostrofo con underscore
  email=d['email']
  print('sto processando ',nome,' ' , cognome)  
  file_name=dirName+"/"+"_".join((nome.title(),cognome,stamp))
  file_name_pdf=corso+"/"+dir_c+"/"+nome+"_"+cognome +'.pdf'
  #print('stampino non modificato ',file_name)
  #print('output to ',file_name_pdf)
  # creo il file che mi servirà per riempire il pdf
  shutil.copy2(template,file_name)
  fin = open(file_name, "rt")
  data = fin.read()
  #replace all occurrences of the required string
  data = data.replace('socio', str(nome + ' ' + cognome))
  #close the input file
  fin.close()
  #open the input file in write mode
  fin = open(file_name, "wt")
  #overrite the input file with the resulting data
  fin.write(data)
  #close the file
  fin.close()
  cmd='pdftk '+ template_pdf+' fill_form '+file_name + ' output '+file_name_pdf 
  
  #print(cmd)
  # adesso che nello stampo fdf ho compilato il socio procedo a creare il pdf
  os.system(cmd)
  
  #  bene è giunto il momento di spedirlo al socio
  # come sopra ma per il corpo della mail
  shutil.copy2('body_template.txt','body.txt')
  fin = open('body.txt', "rt")
  data = fin.read()
  #replace all occurrences of the required string
  data = data.replace('SOCIO', str(nome + ' ' + cognome))
  #close the input file
  fin.close()
  #open the input file in write mode
  fin = open('body.txt', "wt")
  #overrite the input file with the resulting data
  fin.write(data)
  #close the file
  fin.close()
  #email='mauro.biasutti@gmail.com'
  if email== None:
      email='mauro.biasutti@gmail.com'
  cmd='echo "" | mutt -s "Certificato corso PNLUG" -i body.txt -a ' + file_name_pdf + ' --  ' + email
  #print(cmd)
  # adesso spedisco!
  #os.system(cmd)
  time.sleep(1)
  print('certificato inviato a ',nome, ' ' ,cognome)








#sql = """ copy table1 from 's3://bucket/myfile.csv'
    #access_key_id 'xxxx'
    #secret_access_key 'xxx' DELIMITER '\t'
    #timeformat 'auto'
    #maxerror as 250 GZIP IGNOREHEADER 1 """

#cur.execute(sql)


#3

#executemany() takes a list of parameters and each single parameter should be an object that works with execute(), i.e., a tuple or a dict, but not a simple value like a number or string. That's why the second version is OK: you're generating multiple dicts. You can also just write:

#values = [(1,), (2,), (3,)]
#where each element of the list is a tuple.

#share  improve this answer  follow 
