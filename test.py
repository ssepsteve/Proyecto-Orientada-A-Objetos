import sqlite3
import tkinter
def prueba_diccionario():
   diccionario = {1:"Valor 1",
                  "2":["v","a","l","o","r",2],
                  False:{"valor","3"},
                  "4":{"texto:":"valor",
                       "numero":3}
                  }
   for set in diccionario.items():
      llave = set[0]
      valor = set[1]
      print(f"Llave: {llave} Valor: {valor} Tipo De Dato Valor: {type(valor)}")

def prueba_tupla():
   tupla = (3.1416,2.718,6.67E-11)
   for valor in tupla:
      print(valor)

def iterador_multiple():
   tupla = ("1","2","3","4","5")
   for contador, valor in enumerate(tupla):
      print(f"El valor numero: {contador} es el valor en la tupla: {valor}")

def crear_una_tabla():
   direccion_db = r"F:\CODE\Clase POO\Proyecto\Proyecto-Orientada-A-Objetos\base_de_datos.db"
   with sqlite3.connect(direccion_db) as conn:
      cursor = conn.cursor()
      cursor.execute("CREATE TABLE prueba(Id PRIMARY KEY UNIQUE NOT NULL,TEXT texto)")
      conn.commit()
      print("Se ha creado una tabla")

def insertar_valor():
   direccion_db = r"F:\CODE\Clase POO\Proyecto\Proyecto-Orientada-A-Objetos\base_de_datos.db"
   with sqlite3.connect(direccion_db) as conn:
      cursor = conn.cursor()
      cursor.execute("INSERT INTO prueba VALUES(2,'Adios')")
      print("Se ha insertado un valor")

def seleccionar_todo():
   direccion_db = r"F:\CODE\Clase POO\Proyecto\Proyecto-Orientada-A-Objetos\base_de_datos.db"
   with sqlite3.connect(direccion_db) as conn:
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM prueba")
      print("Lo que se ha encontrado en el cursor es: ")
      print(cursor.fetchall())
   
def run_query(query:str, parametros:tuple=()):
   direccion_db = r"F:\CODE\Clase POO\Proyecto\Proyecto-Orientada-A-Objetos\base_de_datos.db"
   with sqlite3.connect(direccion_db) as conn:
      cursor = conn.cursor()
      resultado = cursor.execute(query,parametros)
      conn.commit()
      print(f"Se ha ejecutado el comando:{query} con parametros: {parametros} ")
   return resultado

if __name__ == "__main__":
   ventana = tkinter.Tk()

   ventana.mainloop()


