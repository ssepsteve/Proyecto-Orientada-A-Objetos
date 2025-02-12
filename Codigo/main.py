# !/usr/bin/python3
# -*- coding: utf-8 -*-
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mssg
import sqlite3

class Participantes:
    # nombre de la base de datos  y ruta 
    '''
    El programa debe de ser ejecutado de tal forma que en la terminal de VSCode se encuentre en C:/Direccion/Al/Proyecto/Proyecto-Orientada-A-Objetos
    Mas no en C:/Direccion/Al/Proyecto/Proeecto-Orientada-A-Objetos/Codigo ya que ocurrira un error porque tomara esta direccion como la direccion
    relativa
    '''
    path = r'.' #Path relativo, si se esta ejecutando python en terminal y en el mismo directorio donde esta el Proyecto, se puede dejar
    db_name = path + r'/SQL/Participantes.db' 
    actualiza = None
    tuplaInscripcion = ("Identificacion","Nombre","Direccion","Celular","Entidad","Fecha","Fecha_Inscripcion","Ciudad")
    def __init__(self, master=None):
        # Top Level - Ventana Principal
        self.win = tk.Tk() if master is None else tk.Toplevel()        
        #Top Level - Configuración
        self.win.configure(background="#d9f0f9", relief="flat")
        self.geometria = "1224x600"
        self.win.geometry(self.geometria)
        iconPath = self.path +r'/media/logo.ico'
        self.win.iconbitmap(iconPath)
        self.win.resizable(False, False)
        self.win.title("Conferencia MACSS y la Ingeniería de Requerimientos")
        self.win.pack_propagate(False) 
        
        # Main widget
        self.mainwindow = self.win
        
        #Label Frame
        self.labelsInscripcion = {} #Labes De Inscripcion
        self.entriesInscripcion = {}
        self.lblfrm_Datos = tk.LabelFrame(self.win, width= 700, height= 200, labelanchor= "n", 
                                          font= ("Helvetica", 13,"bold"))

        for iterador in range(0,8):
            self.labelsInscripcion[self.tuplaInscripcion[iterador]] = ttk.Label(self.lblfrm_Datos)
            self.labelsInscripcion[self.tuplaInscripcion[iterador]].configure(anchor="e",font="TkTextFont",justify ="left",text=self.tuplaInscripcion[iterador],width ="12")

            self.entriesInscripcion[self.tuplaInscripcion[iterador]] = tk.Entry(self.lblfrm_Datos)
            self.entriesInscripcion[self.tuplaInscripcion[iterador]].configure(exportselection="false", justify="left",relief="groove", width="30")

        self.entriesInscripcion["Identificacion"].configure(takefocus=True)
        self.entriesInscripcion["Identificacion"].bind("<Key>", self.valida_Identificacion)
        self.entriesInscripcion["Fecha"].bind("<KeyPress>", self.valida_Fecha)
        self.entriesInscripcion["Fecha_Inscripcion"].bind("<KeyPress>",self.valida_Fecha)

        #Placeholder para cuando no se tiene un focus en el entry de fecha y fecha_inscripcion, para que aparezca como un texto de default AAAA-MM-DD
        #Que hace referencia al formato
        self.poner_placeholder(self.entriesInscripcion["Fecha"])
        self.poner_placeholder(self.entriesInscripcion["Fecha_Inscripcion"])
        self.entriesInscripcion["Fecha"].bind("<FocusIn>", self.quitar_placeholder)
        self.entriesInscripcion["Fecha"].bind("<FocusOut>", self.restaurarPlaceholderValidarFecha)
        self.entriesInscripcion["Fecha_Inscripcion"].bind("<FocusIn>",self.quitar_placeholder)
        self.entriesInscripcion["Fecha_Inscripcion"].bind("<FocusOut>",self.restaurarPlaceholderValidarFecha)
        
        for row_iterador in range(0,8):
            self.labelsInscripcion[self.tuplaInscripcion[row_iterador]].grid(column=0,padx="5",pady="15",row=row_iterador,sticky="w")
            self.entriesInscripcion[self.tuplaInscripcion[row_iterador]].grid(column=1, row=row_iterador, sticky="w")

        #Configuración del Labe Frame    
        self.lblfrm_Datos.configure(height="450", relief="groove", text=" Inscripción ", width="330")
        self.lblfrm_Datos.place(anchor="nw", relx="0.01", rely="0.1", width="280", x="0", y="0")
        self.lblfrm_Datos.grid_propagate(False)
        
        self.botones = {}

        config_botones = {
            "Grabar": (self.adiciona_Registro, 0),
            "Editar": (self.edita_tablaTreeView, 80),
            "Eliminar": (self.elimina_Registro, 152),
            "Cancelar": (self.limpia_Campos, 225)
        }

        for texto, (comando, x) in config_botones.items():
            self.botones[texto] = tk.Button(self.win, text=texto, width=9)
            self.botones[texto].place(anchor="nw", rely=0.85, x=x, y=0)
            self.botones[texto].bind("<Enter>",lambda e,button=self.botones[texto]: button.config(background="green",foreground="white"))
            self.botones[texto].bind("<Leave>",lambda e,button=self.botones[texto]: button.config(background="SystemButtonFace",foreground="black"))
            
            if texto == "Cancelar":
                self.botones[texto].configure(command=comando)
            else:
                self.botones[texto].bind("<1>", comando, add="+")
        
        self.botones["Consultar"] = tk.Button(self.win,text="Consultar",width=9)
        self.botones["Consultar"].place(anchor="nw", rely=0.91, x=115, y=0)
        self.botones["Consultar"].bind("<Enter>",lambda e,button=self.botones["Consultar"]: button.config(background="green",foreground="white"))
        self.botones["Consultar"].bind("<Leave>",lambda e,button=self.botones["Consultar"]: button.config(background="SystemButtonFace",foreground="black"))
        self.botones["Consultar"].configure(command=self.botonConsultar)


        #tablaTreeView
        self.style=ttk.Style()
        self.style.configure("estilo.Treeview", highlightthickness=0, bd=0, background='AliceBlue', font=('Calibri Light',10))
        self.style.configure("estilo.Treeview.Heading", background='Azure', font=('Calibri Light', 10,'bold')) 
        self.style.layout("estilo.Treeview", [('estilo.Treeview.treearea', {'sticky': 'nswe'})])

        self.treeDatos = ttk.Treeview(self.win, style="estilo.Treeview")
        # Etiquetas de las columnas
        self.treeDatos["columns"]=("Nombre","Dirección","Celular","Entidad","Fecha","Fecha_Inscripcion","Ciudad")
        
        # Determina el espacio a mostrar que ocupa el código
        columnas = ('Nombre','Dirección','Celular','Entidad','Fecha',"Fecha_Inscripcion","Ciudad")
        self.treeDatos.column('#0',         anchor="w", stretch="true", width=15)
        for i in range(0,7):
            self.treeDatos.column(columnas[i],stretch="true",width=60)
        self.treeDatos.column('Celular',    stretch="true",             width=16)
        self.treeDatos.column('Fecha',      stretch="true",             width=16) 
        self.treeDatos.column('Fecha_Inscripcion',stretch="true",width=80)
        self.treeDatos.column('Ciudad',stretch="true",width=10)

       #Encabezados de las columnas de la pantalla
        self.treeDatos.heading('#0',       text = 'Id')
        for i in range(0,7):
            self.treeDatos.heading(columnas[i],text=columnas[i])

        #Scrollbar en el eje Y de treeDatos
        self.scrollbar=ttk.Scrollbar(self.win, orient='vertical', command=self.treeDatos.yview)
        self.treeDatos.configure(yscroll=self.scrollbar.set)
        self.scrollbar.place(x=1200, y=50, height=400)

        #Carga los datos en treeDatos
        self.lee_tablaTreeView()    
        self.treeDatos.place(anchor="nw", height="450", rely="0.1", width="900", x="300", y="0")
 
   
    def valida(self):
        '''Valida que el Id no esté vacio, devuelve True si ok'''
        return (len(self.entriesInscripcion["Identificacion"].get()) != 0 )   

    def run(self):
        '''Se Centra Primero La Ventana Y Luego Se Ejecuta'''
        anchoPantalla = self.mainwindow.winfo_screenwidth()
        alturaPantalla = self.mainwindow.winfo_screenheight()
        anchoVentana = self.mainwindow.winfo_width()
        alturaVentana = self.mainwindow.winfo_height()
        posicionEsquinaX = int(anchoPantalla/2-anchoVentana/2)
        posicionEsquinaY = int(alturaPantalla/2-alturaVentana/2)
        self.mainwindow.geometry(self.geometria+f"+{posicionEsquinaX}+{posicionEsquinaY}")

        self.mainwindow.mainloop()

    def valida_Identificacion(self, event=None):
        ''' Valida que la longitud no sea mayor a 15 caracteres'''
        if event.char.isdigit():
            if len(self.entriesInscripcion["Identificacion"].get()) >= 15:
                mssg.showerror('Atención!!','.. ¡Máximo 15 caracteres! ..')
                self.entriesInscripcion["Identificacion"].delete(15,"end")
        else:
              self.entriesInscripcion["Identificacion"].delete(15,"end")

    def poner_placeholder(self,entry):
        """Coloca el texto en gris si el campo está vacío."""
        if entry.get() == "":
            entry.insert(0, "AAAA-MM-DD")  # Texto de ejemplo
            entry.config(fg="gray")

    def quitar_placeholder(self,event):
        """Elimina el texto gris cuando el usuario hace clic en el Entry."""
        if event.widget.get() == "AAAA-MM-DD":
            event.widget.delete(0, tk.END)
            event.widget.config(fg="black")  # Cambia el color al escribir

    def restaurar_placeholder(self,event):
        """Restaura el texto gris si el usuario no escribió nada."""
        if event.widget.get() == "":
            self.poner_placeholder(event.widget)
    
    def __dia_existente(self,año:int,mes:str,dia:int):
        meses_dias = {
        "01": 31, "02": 28, "03": 31, "04": 30, "05": 31, "06": 30,
        "07": 31, "08": 31, "09": 30, "10": 31, "11": 30, "12": 31
        }
        if mes == "02" and (año % 4 == 0 and (año % 100 != 0 or año % 400 == 0)):
            meses_dias["02"] = 29
        # Verificar si el día es válido
        return 1 <= dia <= meses_dias[mes]   
    
    def __fecha_valida(self,entry): #AAAA-MM-DD
        strEntry = entry.get()
        año = int(strEntry[0:4])
        mesStr = strEntry[5:7]
        dia = int(strEntry[8:10])
        if len(strEntry) == 10:
            if 0<año <=2025:
                if 1<=int(mesStr) <=12:
                    if 1<=dia <=31:
                        return self.__dia_existente(año,mesStr,dia)
                else: return False
            else: return False
        else: return False

    def restaurarPlaceholderValidarFecha(self,event):
        if event.widget.get() != '' or not self.__fecha_valida(event.widget):
            mssg.showerror("Fecha Invalida","El Campo De Fecha Es Invalido")
        else:
            self.restaurar_placeholder(event)

    def valida_Fecha(self, event=None): #POR IMPLEMENTAR
        if event.char.isdigit():
            if len(event.widget.get())==10:
                event.widget.delete(0,tk.END)
            else:
                if len(event.widget.get())==4 or len(event.widget.get())==7:
                    event.widget.insert(tk.END,"-")
                else:
                    pass
        else:
            event.widget.delete(10,"end")
    
    def carga_Datos(self):
        ''' Carga los datos en los campos desde el treeView'''
        self.entriesInscripcion["Identificacion"].configure(state="normal")
        self.entriesInscripcion["Identificacion"].delete(0,tk.END)
        self.entriesInscripcion["Identificacion"].insert(0,self.treeDatos.item(self.treeDatos.selection())['text'])
        self.entriesInscripcion["Identificacion"].configure(state = 'readonly')
        for i in range(1,8):
            self.entriesInscripcion[self.tuplaInscripcion[i]].insert(0,self.treeDatos.item(self.treeDatos.selection())['values'][i-1])
              
    def limpia_Campos(self): #POR IMPLEMENTAR
        self.entriesInscripcion["Identificacion"].configure(state="normal")
        for entry in self.entriesInscripcion.values():
            entry.delete(0,tk.END)
        #self.entriesInscripcion["Fecha"].insert(0,"Fecha En AAAA-MM-DD")
        #self.entriesInscripcion["Fecha_Inscripcion"].insert(0,"Fecha En AAAA-MM-DD")

    def botonConsultar(self,event=None):
        campoId = self.entriesInscripcion["Identificacion"].get()
        if campoId in (""," "):
            mssg.showerror("Id Vacio","El Campo De Identificacion Esta Vacio")
        else:
            query = "SELECT Id FROM t_participantes"
            retCursor = self.run_Query(query)
            cursorList = [str(row[0]) for row in retCursor]
            if campoId in cursorList:
                pass #IMPLEMENTACION DE PASAR DATOS DE LA BASE DE DATOS AL CAMPO INSCRIPCION
            else:
                mssg.showerror("Id No Encontrado",f"El Id:{campoId} No Fue Encontrado En La Base De Datos")


    def run_Query(self, query, parametros = ()):
        ''' Función para ejecutar los Querys a la base de datos '''
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parametros)
            conn.commit()
        return result

    def lee_tablaTreeView(self):
        ''' Carga los datos de la BD y Limpia la Tabla tablaTreeView '''
        tabla_TreeView = self.treeDatos.get_children()
        for linea in tabla_TreeView:
            self.treeDatos.delete(linea) #Limpia los datos que habian antes del treeview
        # Seleccionando los datos de la BD
        query = 'SELECT * FROM t_participantes ORDER BY Id DESC'
        db_rows = self.run_Query(query)
        # Insertando los datos de la BD en la tabla de la pantalla
        for row in db_rows:
            self.treeDatos.insert('',0, text = row[0], values = [row[1],row[2],row[3],row[4],row[5],row[6],row[7]])
        
    def adiciona_Registro(self, event=None):
        '''Adiciona un producto a la BD si la validación es True'''
        if self.actualiza:
            self.actualiza = None
            self.entriesInscripcion["Identificacion"].configure(state = 'readonly')
            query = 'UPDATE t_participantes SET Id = ?,Nombre = ?,Direccion = ?,Celular = ?, Entidad = ?, Fecha = ?, Fecha_Inscripcion = ?, Ciudad = ? WHERE Id = ?'
            parametros = (self.entriesInscripcion["Identificacion"].get(), self.entriesInscripcion["Nombre"].get(), self.entriesInscripcion["Direccion"].get(),
                          self.entriesInscripcion["Celular"].get(), self.entriesInscripcion["Entidad"].get(), self.entriesInscripcion["Fecha"].get(),
                          self.entriesInscripcion["Fecha_Inscripcion"].get(),self.entriesInscripcion["Ciudad"].get(),
                          self.entriesInscripcion["Identificacion"].get()
                          )
                        #   self.entriesInscripcion["Identificacion"].get())
            self.run_Query(query, parametros)
            mssg.showinfo('Ok',' Registro actualizado con éxito')
        else:
            query = 'INSERT INTO t_participantes VALUES(?, ?, ?, ?, ?, ?,?,?)'
            parametros = (self.entriesInscripcion["Identificacion"].get(),self.entriesInscripcion["Nombre"].get(), self.entriesInscripcion["Direccion"].get(),
                          self.entriesInscripcion["Celular"].get(), self.entriesInscripcion["Entidad"].get(), self.entriesInscripcion["Fecha"].get(),
                          self.entriesInscripcion["Fecha_Inscripcion"].get(),self.entriesInscripcion["Ciudad"].get()
                          )
            if self.valida():
                self.run_Query(query, parametros)
                mssg.showinfo('',f'Registro: {self.entriesInscripcion["Identificacion"].get()} .. agregado')
                self.limpia_Campos()
            else:
                mssg.showerror("¡ Atención !","No puede dejar la identificación vacía")
        self.limpia_Campos()
        self.lee_tablaTreeView()

    def edita_tablaTreeView(self, event=None):
        try:
            # Carga los campos desde la tabla TreeView
            self.treeDatos.item(self.treeDatos.selection())['text']
            self.limpia_Campos()
            self.actualiza = True # Esta variable controla la actualización
            self.carga_Datos()
        except IndexError as error:
            self.actualiza = None # Por que no False?
            mssg.showerror("¡ Atención !",'Por favor seleccione un ítem de la tabla')
            return
                
    def elimina_Registro(self, event=None):
        if len(self.entriesInscripcion["Identificacion"].get())!=0:
            if mssg.askyesno("Advertencia","Esta seguro que quiere borrar el dato de la base de datos?"):
                query = "DELETE FROM t_participantes WHERE Id=?"
                parametros = (self.entriesInscripcion["Identificacion"].get(),)
                with sqlite3.connect(self.db_name) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1 FROM t_participantes WHERE Id=?",parametros)
                    if cursor.fetchone():
                        result = cursor.execute(query, parametros)
                        conn.commit()
                        mssg.showinfo("Registro Eliminado","El Registro Ha Sido Eliminado De La Base De Datos")
                        self.limpia_Campos()
                        self.lee_tablaTreeView()
                    else:
                        mssg.showerror("Registro No Encontrado","El Registro No Ha Sido Encontrado En La Base De Datos")
            else:
                pass
        else:
            mssg.showinfo("Campo Vacio","El Campo De Identificacion Esta Vacio")

if __name__ == "__main__":
    app = Participantes()
    app.run()