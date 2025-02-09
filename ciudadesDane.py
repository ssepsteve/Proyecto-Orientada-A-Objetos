import csv
import sqlite3

path = r"."
csvPath = path+r"/Departamentos_y_municipios_de_Colombia_20250209.csv"
dbPath = path+r"/SQL/Participantes.db"

def run_query(query,parametros):    
    with sqlite3.connect(dbPath) as conn:
        cursor = conn.cursor()
        result = cursor.execute(query, parametros)
        conn.commit()
    return result

with open(csvPath,newline='',encoding="utf8")as csvfile:
    reader = csv.DictReader(csvfile,delimiter=',',quotechar='|')
    for row in reader:
        parametros = (row["CÓDIGO DANE DEL DEPARTAMENTO"],row["CÓDIGO DANE DEL MUNICIPIO"],row["DEPARTAMENTO"],row["MUNICIPIO"])
        run_query('INSERT INTO t_ciudades VALUES(?, ?, ?, ?)',parametros)

