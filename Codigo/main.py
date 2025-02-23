# !/usr/bin/python3
# -*- coding: utf-8 -*-
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mssg
import sqlite3
import re

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
    tupla_inscripcion = ("Identificacion","Nombre","Direccion","Celular","Entidad","Fecha","Fecha_Inscripcion","Ciudad")
    def __init__(self, master=None):
        # Top Level - Ventana Principal
        self.win = tk.Tk() if master is None else tk.Toplevel()  
        self.color_sin_hover = "#FAEDCD"      
        #Top Level - Configuración
        self.color_default = "#FEFAE0"
        self.win.configure(background=self.color_default, relief="flat")
        self.geometria = "1224x600"
        self.win.geometry(self.geometria)
        icon_path = self.path +r'/media/logo.ico'
        self.win.iconbitmap(icon_path)
        self.win.resizable(False, False)
        self.win.title("Conferencia MACSS y la Ingeniería de Requerimientos")
        self.win.pack_propagate(False) 
        
        # Main widget
        self.mainwindow = self.win
        
        #Label Frame
        self.labels_inscripcion = {} #Labes De Inscripcion
        self.entries_inscripcion = {}
        self.botones = {}
        self.color_inscripcion = "#E9EDC9"
        self.lblfrm_Datos = tk.LabelFrame(self.win, width= 700, height= 180, labelanchor= "n", 
                                          font= ("Helvetica", 13,"bold"),bg=self.color_inscripcion)

        for idx, campo in enumerate(self.tupla_inscripcion):
            # Crear y configurar labels
            self.labels_inscripcion[campo] = ttk.Label(self.lblfrm_Datos, anchor="e", font="TkTextFont", justify="left", text=campo, width=12,background=self.color_inscripcion)
            self.labels_inscripcion[campo].grid(column=0, padx=5, pady=15, row=idx, sticky="w")
            # Crear y configurar entries
            self.entries_inscripcion[campo] = tk.Entry(self.lblfrm_Datos, exportselection=False, justify="left", relief="groove", width=30)
            self.entries_inscripcion[campo].grid(column=1, row=idx, sticky="w")

        #Configuracion especificas
        self.entries_inscripcion["Identificacion"].configure(takefocus=True)
        self.entries_inscripcion["Ciudad"].configure(width=15,state="readonly") 
        self.entries_inscripcion["Identificacion"].bind("<Key>", self.valida_Identificacion)
        self.entries_inscripcion["Celular"].bind("<Key>",self.aceptar_solo_numeros)
    
        #Placeholder para cuando no se tiene un focus en el entry de fecha y fecha_inscripcion, para que aparezca como un texto de default AAAA-MM-DD
        #Que hace referencia al formato
        for campo in ("Fecha","Fecha_Inscripcion"):
            entry = self.entries_inscripcion[campo]
            self.poner_placeholder(entry)
            entry.bind("<KeyPress>",self.valida_Fecha)
            entry.bind("<FocusIn>", self.quitar_placeholder)
            entry.bind("<FocusOut>",self.restaurar_placeholder_validarfecha)
        
        #Configuración del Labe Frame    
        self.lblfrm_Datos.configure(height="450", relief="groove", text=" Inscripción ", width="330")
        self.lblfrm_Datos.place(anchor="nw", relx="0.01", rely="0.1", width="280", x="0", y="0")
        self.lblfrm_Datos.grid_propagate(False)
        self.botones["Buscar"] = tk.Button(self.lblfrm_Datos,text="Buscar",width=5,height=1,command=self.abrir_ventana_busqueda)
        self.botones["Buscar"].place(x=225,rely=0.92)

        #Configuracion Botones CRUD
        config_botones = {
            "Grabar": (self.adiciona_Registro, 0),
            "Editar": (self.edita_tablaTreeView, 80),
            "Eliminar": (self.elimina_registro, 152),
            "Cancelar": (self.limpia_campos, 225)
        }

        for texto, (comando, x) in config_botones.items():
            self.botones[texto] = tk.Button(self.win, text=texto, width=9)
            self.botones[texto].place(anchor="nw", rely=0.85, x=x, y=0)
            if texto == "Cancelar":
                self.botones[texto].configure(command=comando)
            else:
                self.botones[texto].bind("<1>", comando, add="+")
        
        self.botones["Consultar"] = tk.Button(self.win,text="Consultar",width=9)
        self.botones["Consultar"].place(anchor="nw", rely=0.91, x=115, y=0)
        self.botones["Consultar"].configure(command=self.boton_consultar)

        for boton in self.botones.values():
            boton.config(background=self.color_sin_hover)

        for boton in self.botones.values(): self.ligar_evento_hover(boton=boton)

        #tablaTreeView
        self.style=ttk.Style()
        self.style.configure("estilo.Treeview", highlightthickness=0, bd=0, background='#e8f0c9', font=('Calibri Light',10))
        self.style.configure("estilo.Treeview.Heading", background='#148f54', font=('Calibri Light', 10,'bold')) 
        self.style.layout("estilo.Treeview", [('estilo.Treeview.treearea', {'sticky': 'nswe'})])

        self.tree_datos = ttk.Treeview(self.win, style="estilo.Treeview")
        # Etiquetas de las columnas
        columnas = ('Nombre','Dirección','Celular','Entidad','Fecha',"Fecha_Inscripcion","Ciudad")
        self.tree_datos["columns"]=columnas
        # Determina el espacio a mostrar que ocupa el código
        self.tree_datos.column('#0',         anchor="w", stretch="true", width=15)
        self.tree_datos.heading('#0',       text = 'Id')
        
        anchos_columnas = {"Nombre": 60, "Dirección": 60, "Celular": 16, "Entidad": 60, "Fecha": 16, "Fecha_Inscripcion": 80, "Ciudad": 10}

        for columna in columnas:
            self.tree_datos.column(columna, stretch=True, width=anchos_columnas.get(columna, 60))
            self.tree_datos.heading(columna, text=columna)

        #Scrollbar en el eje Y de tree_datos
        self.scrollbar=ttk.Scrollbar(self.win, orient='vertical', command=self.tree_datos.yview)
        self.tree_datos.configure(yscroll=self.scrollbar.set)
        self.scrollbar.place(x=1200, y=50, height=400)

        #Carga los datos en tree_datos
        self.lee_tablaTreeView()    
        self.tree_datos.place(anchor="nw", height="450", rely="0.1", width="900", x="300", y="0")
   
    def valida(self):
        '''Valida que el Id no esté vacio, devuelve True si ok'''
        return (len(self.entries_inscripcion["Identificacion"].get()) != 0 )   

    def run(self):
        """Centra la ventana y la ejecuta."""
        self.mainwindow.update_idletasks()  # Asegura que winfo_width y winfo_height devuelvan valores correctos
        ancho_pantalla = self.mainwindow.winfo_screenwidth()
        altura_pantalla = self.mainwindow.winfo_screenheight()
        ancho_ventana = self.mainwindow.winfo_width()
        altura_ventana = self.mainwindow.winfo_height()

        posicion_esquina_x = (ancho_pantalla - ancho_ventana) // 2
        posicion_esquina_y = (altura_pantalla - altura_ventana) // 2

        self.mainwindow.geometry(f"{ancho_ventana}x{altura_ventana}+{posicion_esquina_x}+{posicion_esquina_y}")
        self.mainwindow.deiconify()
        self.mainwindow.mainloop()

    #Manejo De Eventos

    def ligar_evento_hover(self,boton:tk.Button):
        color_en_hover = "#D4A373"
        boton.bind("<Enter>",lambda e,boton=boton: boton.config(background=color_en_hover,foreground="white"))
        boton.bind("<Leave>",lambda e,boton=boton: boton.config(background=self.color_sin_hover,foreground="black"))

    def aceptar_solo_numeros(self,event:tk.Event):
        ''' Revisa si el caracter relacionado al evento de teclado sea un numero, en  casto tal de que no, devuelve "break" para 
            romper la ejecucion tras el evento, por ejemplo si el usuario pone un caracter en una entrada como fecha un caracter,
            se devuelve "break" para que no sea puesto el caracter en el entry, tambien maneja el caso en el que se haga uso de la 
            tecla de backspace, ya que al tener esta un ASCII de 8 (por esto se hace uso de ord), se verifica si se ha oprimido
            esta tecla para que no se devuelva "break", tambien en caso tal de que se oprima una tecla como caps lock que no tiene
            un string relacionado, se maneje de forma tal de que se devuelva un "break"  '''
        if len(event.char) == 0: return "break"
        elif not event.char.isdigit() and ord(event.char) != 8:return "break" #ord devuelve el codigo ASCII de un caracter
        else:return None

    def valida_Identificacion(self, event:tk.Event=None):
        ''' Valida que la longitud no sea mayor a 15 caracteres'''
        validar = self.aceptar_solo_numeros(event=event)
        if validar == "break":return validar
        elif event.char.isdigit():
            if len(self.entries_inscripcion["Identificacion"].get()) >= 15:
                mssg.showerror('Atención!!','.. ¡Máximo 15 caracteres! ..')
        
        self.entries_inscripcion["Identificacion"].delete(15,"end") #Borra el caracter numero 15 si es que existe

    def poner_placeholder(self,entry,texto:str="AAAA-MM-DD"):
        """Coloca el texto en gris si el campo está vacío."""
        if entry.get() == "":
            entry.insert(0,texto)  # Texto de ejemplo
            entry.config(fg="gray")

    def quitar_placeholder(self,event:tk.Event=None,entry:tk.Entry=None,texto:str="AAAA-MM-DD"):
        """Elimina el texto gris cuando el usuario hace clic en el Entry."""
        if event == None:
            if entry.get() == texto:
                entry.delete(0, tk.END)
                entry.config(fg="black")
        else:
            if event.widget.get() == texto:
                event.widget.delete(0, tk.END)
                event.widget.config(fg="black")  # Cambia el color al escribir

    def restaurar_placeholder(self,event:tk.Event=None,entry:tk.Entry=None,texto:str="AAAA-MM-DD"):
        """Restaura el texto gris si el usuario no escribió nada."""
        if event == None:
            if entry.get() == "":
                self.poner_placeholder(entry,texto)
        else:
            if event.widget.get() == "":
                self.poner_placeholder(event.widget,texto)
    
    def __dia_existente(self,año:int,mes:str,dia:int):
        '''Revisa si una fecha especificada es posible que exista, siempre y cuando esta sea antes del año
           actual(2025)'''
        meses_dias = {
        "01": 31, "02": 28, "03": 31, "04": 30, "05": 31, "06": 30,
        "07": 31, "08": 31, "09": 30, "10": 31, "11": 30, "12": 31
        }
        if mes == "02" and (año % 4 == 0 and (año % 100 != 0 or año % 400 == 0)):
            meses_dias["02"] = 29
        # Verificar si el día es válido
        return 1 <= dia <= meses_dias[mes]   
    
    def __fecha_valida(self,entry): 
        '''Descarta antes si la entrada del entry es valida para una fecha, revisa si 
        el entry tenga 10 caracteres, y que los años, meses y dias esten en el intervalo posible
        como años menores o iguales a 2025 y mayores a 0, meses menores o iguales a 12 y mayores o iguales a 1
        y dias menos o iguales a 31 y mayores o iguales 1'''
        strEntry = entry.get()
        if strEntry not in (""," ","AAAA-MM-DD"):
            if len(strEntry) != 10:
                return False
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
        return True

    def restaurar_placeholder_validarfecha(self,event:tk.Event):
        '''Manda un mensaje de error en caso tal de que la fecha no sea valida'''
        if not self.__fecha_valida(event.widget):
            mssg.showerror("Fecha Invalida","El Campo De Fecha Es Invalido")
        else:
            self.restaurar_placeholder(event=event) #En caso tal de que la longitud de los caracteres en el string sea igual a 1 o 0

    def valida_Fecha(self, event:tk.Event=None): #POR IMPLEMENTAR
        '''Se encarga de dar el formato automatico de AAAA-MM-DD osea pone los guiones'''
        validar = self.aceptar_solo_numeros(event=event)
        if validar == "break":
            return "break"
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
    
    def edita_tablaTreeView(self, event=None):
        ''' Se encarga de ejecutar una rutina para cargar los datos de edicion a la seccion
            de inscripcion'''
        try:
            # Carga los campos desde la tabla TreeView
            self.limpia_campos()
            self.actualiza = True # Esta variable controla la actualización
            self.carga_Datos()
        except IndexError as error:
            self.actualiza = None # Por que no False?
            mssg.showerror("¡ Atención !",'Por favor seleccione un ítem de la tabla')
            return

    def carga_Datos(self):
        ''' Carga los datos en la seccion de inscripcion al hacer uso del treeView, en el campo seleccionado'''
        seleccion = self.tree_datos.selection()
        
        item = self.tree_datos.item(seleccion[len(seleccion)-1])
        identificacion = item['text']
        valores = item['values']

        self.entries_inscripcion["Identificacion"].configure(state="normal")
        self.entries_inscripcion["Ciudad"].configure(state="normal")

        self.entries_inscripcion["Identificacion"].delete(0, tk.END)
        self.entries_inscripcion["Identificacion"].insert(0, identificacion)

        for campo, valor in zip(self.tupla_inscripcion[1:], valores):
            self.entries_inscripcion[campo].delete(0, tk.END)
            self.entries_inscripcion[campo].insert(0, valor)

        self.entries_inscripcion["Fecha_Inscripcion"].configure(fg="black")
        self.entries_inscripcion["Fecha"].configure(fg="black")

        self.entries_inscripcion["Identificacion"].configure(state='readonly')
        self.entries_inscripcion["Ciudad"].configure(state="readonly")
              
    def limpia_campos(self):
        ''' Borra todo lo que se encuentra en la seccion de inscripcion pero manteniendo
            el estado de readonly de Ciudad y los placeholders de las fechas
        '''
        self.entries_inscripcion["Identificacion"].configure(state="normal")
        self.entries_inscripcion["Ciudad"].configure(state="normal")

        self.quitar_placeholder(entry=self.entries_inscripcion["Fecha_Inscripcion"])
        self.quitar_placeholder(entry=self.entries_inscripcion["Fecha"])
        
        for entry in self.entries_inscripcion.values():
            entry.delete(0,tk.END)
        
        self.entries_inscripcion["Ciudad"].configure(state="readonly")
        self.restaurar_placeholder(entry=self.entries_inscripcion["Fecha_Inscripcion"])
        self.restaurar_placeholder(entry=self.entries_inscripcion["Fecha"])

    def boton_consultar(self,event=None):
        ''' Carga los datos de la base de datos dependiendo de que es puesto
            en la seccion de identificacion y si es capaz de encontrar el id en cuestion
        '''
        campo_id = self.entries_inscripcion["Identificacion"].get()
        if campo_id in (""," "):
            mssg.showerror("Id Vacio","El Campo De Identificacion Esta Vacio")
        else:
            query = "SELECT Id FROM t_participantes"
            return_cursor = self.run_query(query)
            cursor_list = [str(row[0]) for row in return_cursor]
            if campo_id in cursor_list:
                query = f"SELECT * FROM t_participantes WHERE Id=?"
                parametros = (campo_id,)
                cursor = self.run_query(query,parametros)
                cursor_list = [str(j) for i in cursor for j in i]
                for indice, entry in enumerate(self.entries_inscripcion.values()):
                    entry.configure(state="normal")
                    entry.delete(0,tk.END)
                    entry.insert(0,cursor_list[indice])
                self.entries_inscripcion["Fecha_Inscripcion"].configure(fg="black")
                self.entries_inscripcion["Fecha"].configure(fg="black")
                self.entries_inscripcion["Identificacion"].configure(state="readonly")
                self.entries_inscripcion["Ciudad"].configure(state="readonly")
            else:
                mssg.showerror("Id No Encontrado",f"El Id: {campo_id} No Fue Encontrado En La Base De Datos")

    def run_query(self, query:str, parametros:tuple = ()):
        ''' Función para ejecutar los Querys a la base de datos y retornar un cursor'''
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parametros)
            conn.commit()
        return result

    def lee_tablaTreeView(self):
        ''' Limpia la Tabla tablaTreeView y Carga los datos de la BD '''
        tabla_treeView = self.tree_datos.get_children()
        for linea in tabla_treeView:
            self.tree_datos.delete(linea) #Limpia los datos que habian antes del treeview
        # Seleccionando los datos de la BD
        query = 'SELECT * FROM t_participantes ORDER BY Id DESC'
        db_rows = self.run_query(query)
        # Insertando los datos de la BD en la tabla de la pantalla
        for row in db_rows:
            self.tree_datos.insert('',0, text = row[0], values = [row[1],row[2],row[3],row[4],row[5],row[6],row[7]])

    def id_existente(self,id:str) -> bool:
        '''Revisa si un id ya se encuentra dentro de la base de datos'''
        query = "SELECT Id FROM t_participantes"
        resultados = [str(row[0]) for row in self.run_query(query)]
        return id in resultados

    def adiciona_Registro(self, event=None):
        '''Adiciona un producto a la BD si la validación es True'''
        id = self.entries_inscripcion["Identificacion"].get()
        self.actualiza = self.id_existente(id)
        if self.actualiza:
            if mssg.askyesno("Identificacion Existente", f"La Identificacion: {id} Ya Existe En La Base De Datos, Desea Actualizarla?"):
                self.actualiza = None
                self.entries_inscripcion["Identificacion"].configure(state = 'readonly')
                query = 'UPDATE t_participantes SET Id = ?,Nombre = ?,Direccion = ?,Celular = ?, Entidad = ?, Fecha = ?, Fecha_Inscripcion = ?, Ciudad = ? WHERE Id = ?'
                parametros = (self.entries_inscripcion["Identificacion"].get(), self.entries_inscripcion["Nombre"].get(), self.entries_inscripcion["Direccion"].get(),
                            self.entries_inscripcion["Celular"].get(), self.entries_inscripcion["Entidad"].get(), self.entries_inscripcion["Fecha"].get(),
                            self.entries_inscripcion["Fecha_Inscripcion"].get(),self.entries_inscripcion["Ciudad"].get(),
                            self.entries_inscripcion["Identificacion"].get()
                            )
                            #   self.entries_inscripcion["Identificacion"].get())
                self.run_query(query, parametros)
                mssg.showinfo('Ok',' Registro actualizado con éxito')
        else:
            query = 'INSERT INTO t_participantes VALUES(?, ?, ?, ?, ?, ?,?,?)'
            parametros = (self.entries_inscripcion["Identificacion"].get(),self.entries_inscripcion["Nombre"].get(), self.entries_inscripcion["Direccion"].get(),
                          self.entries_inscripcion["Celular"].get(), self.entries_inscripcion["Entidad"].get(), self.entries_inscripcion["Fecha"].get(),
                          self.entries_inscripcion["Fecha_Inscripcion"].get(),self.entries_inscripcion["Ciudad"].get()
                          )
            if self.valida():
                self.run_query(query, parametros)
                mssg.showinfo('',f'Registro: {self.entries_inscripcion["Identificacion"].get()} .. agregado')
            else:
                mssg.showerror("¡ Atención !","No puede dejar la identificación vacía")
                return
        self.limpia_campos()
        self.lee_tablaTreeView()
               
    def elimina_registro(self, event=None):
        selecciones = self.tree_datos.selection()
        if len(selecciones)>0:
            if mssg.askyesno("Advertencia","Esta seguro que quiere borrar los datos seleccionados de la base de datos?"):
                items = []
                for seleccion in selecciones:
                    items.append(self.tree_datos.item(seleccion))
                for item in items:
                    id = item["text"]
                    query = "DELETE FROM t_participantes WHERE Id=?"
                    parametros = (id,)
                    self.run_query(query,parametros)

                mssg.showinfo("Registros Eliminados","Los Registros Han Sido Eliminado De La Base De Datos")
                self.lee_tablaTreeView()
        elif len(self.entries_inscripcion["Identificacion"].get())!=0:
            if mssg.askyesno("Advertencia","Esta seguro que quiere borrar el dato de la base de datos?"):
                query = "DELETE FROM t_participantes WHERE Id=?"
                parametros = (self.entries_inscripcion["Identificacion"].get(),)
                with sqlite3.connect(self.db_name) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1 FROM t_participantes WHERE Id=?",parametros)
                    if cursor.fetchone():
                        result = cursor.execute(query, parametros)
                        conn.commit()
                        mssg.showinfo("Registro Eliminado","El Registro Ha Sido Eliminado De La Base De Datos")
                        self.limpia_campos()
                        self.lee_tablaTreeView()
                    else:
                        mssg.showerror("Registro No Encontrado","El Registro No Ha Sido Encontrado En La Base De Datos")
            else:
                pass
        else:
            mssg.showinfo("Campo Vacio","El Campo De Identificacion Esta Vacio")

#VENTANA BUSQUEDA

    def abrir_ventana_busqueda(self):
        '''Crea la subventana de busqueda cuando el boton de buscar es presionado'''
        path_icono_lupa = self.path+r"/Media/Lupa.ico"
        self.win_busqueda = tk.Toplevel()
        self.win_busqueda.geometry("700x500")
        self.win_busqueda.resizable(False,False)
        self.win_busqueda.title("Buscar Ciudad")
        self.win_busqueda.iconbitmap(path_icono_lupa)
        self.win_busqueda.configure(background=self.color_default)

        #Creacion Y Posicion Frames
        self.frame_entry = tk.Frame(self.win_busqueda,width=700,height=50,bg=self.color_default)
        self.frame_tabla = ttk.Frame(self.win_busqueda,width=700,height=400,style="estilo.Treeview")
        self.frame_botones = tk.Frame(self.win_busqueda,width=700,height=50,bg=self.color_default)
        self.frame_botones.columnconfigure((0,1,2,3),weight=1)

        self.frame_entry.grid(row=0,column=0,sticky="nsew")
        self.frame_tabla.grid(row=1,column=0,sticky="nsew")
        self.frame_botones.grid(row=2,column=0,sticky="nsew")

        ### MODIFICACIONES EN FRAME_eNTRY ###
        #Creacion Entry Busqueda
        self.entry_busqueda = tk.Entry(self.frame_entry)
        texto_place_holder = "Buscar Por Ciudad, Departamento o Ids"
        self.poner_placeholder(entry=self.entry_busqueda,texto=texto_place_holder)
        self.entry_busqueda.bind("<FocusIn>",lambda e, texto = texto_place_holder, entry = self.entry_busqueda:self.quitar_placeholder(entry=entry,texto=texto))
        self.entry_busqueda.bind("<FocusOut>",lambda e, texto = texto_place_holder, entry = self.entry_busqueda:self.restaurar_placeholder(entry=entry,texto=texto))
        self.entry_busqueda.pack(expand=True,fill="both")


        ### MODIFICACIONES EN FRAME_tABLA ###
        #Creacion Tabla Busqueda
        self.tabla_busqueda = ttk.Treeview(self.frame_tabla,style="estilo.Treeview")
        # Etiquetas de las columnas
        self.tabla_busqueda["columns"]=("Id_Departamento","Departamento","Ciudad")
        
        # Determina el espacio a mostrar que ocupa el código
        columnas = ("Id_Departamento","Departamento","Ciudad")
        self.tabla_busqueda.column('#0',         anchor="w", stretch="true", width=80)
        for columna in columnas:
            self.tabla_busqueda.column(columna,stretch="true",width=180)

       #Encabezados de las columnas de la pantalla
        self.tabla_busqueda.heading('#0',       text = 'Id_Ciudad')
        for columna in columnas:
            self.tabla_busqueda.heading(columna,text=columna)

        #Scrollbar en el eje Y de tree_datos
        self.scrollbar=ttk.Scrollbar(self.win_busqueda, orient='vertical', command=self.tabla_busqueda.yview)
        self.tabla_busqueda.configure(yscroll=self.scrollbar.set)
        self.scrollbar.place(x=680, y=0, height=500)
        self.lee_tabla_busqueda()
        self.tabla_busqueda.place(height=400,x=40)


        ### MODIFICACIONES EN FRAME_bOTONES ###
        #Creacion Labels, Entries Y Botones
        self.label_ciudad = tk.Label(self.frame_botones,text="Ciudad: ",bg=self.color_default)
        self.entry_ciudad = tk.Entry(self.frame_botones,state="readonly",bg=self.color_default)
        self.label_departamento = tk.Label(self.frame_botones,text="Departamento: ",bg=self.color_default)
        self.entry_departamento = tk.Entry(self.frame_botones,state="readonly",bg=self.color_default)
        self.boton_buscar = tk.Button(self.frame_botones,text="Buscar Ciudad/Departamento",command=self.boton_buscar_ciudad,background=self.color_sin_hover)
        self.boton_insertar = tk.Button(self.frame_botones,text="Insertar",command=self.boton_insertar_busqueda,background=self.color_sin_hover)
        self.boton_grabarCiudad = tk.Button(self.frame_botones,text="Grabar Ciudad",command=self.boton_grabar_ciudad,background=self.color_sin_hover)

        #Agregar Cambios De Color A Los Botones Con Hover
        self.ligar_evento_hover(self.boton_buscar)
        self.ligar_evento_hover(self.boton_insertar)
        self.ligar_evento_hover(self.boton_grabarCiudad)

        #Posicionamiento En Grilla De Los Botones
        self.label_ciudad.grid(row=0,column=0)
        self.entry_ciudad.grid(row=0,column=1)
        self.label_departamento.grid(row=0,column=2)
        self.entry_departamento.grid(row=0,column=3)
        self.boton_buscar.grid(row=1,column=0,columnspan=2)
        self.boton_insertar.grid(row=1,column=2)
        self.boton_grabarCiudad.grid(row=1,column=3)

    def diccionario_posible_busqueda(self,query:str) -> dict:
        ''' Devuelve un diccionario con los posibles resultados de una busqueda en el diccionario
            self.diccionario_tabla_ciudades, query hace referencia a lo que se quiere buscar, ya sea una
            ciudad, departamento o basandose en los ids de las ciudades y departamentos'''
        patron = re.compile(re.escape(query), re.IGNORECASE)

        resultados = {}

        for ciudad_id, info in self.diccionario_tabla_ciudades.items():
            # Buscar en ID de ciudad, número de departamento, nombre de departamento o ciudad
            if (
                patron.search(ciudad_id) or
                patron.search(info["Id_Departamento"]) or
                patron.search(info["Departamento"]) or
                patron.search(info["Ciudad"])
            ):
                resultados[ciudad_id] = info

        return resultados

    def boton_buscar_ciudad(self):
        ''' Se encarga de dar la utilidad del boton buscar ciudad/departamento'''
        buscar = self.entry_busqueda.get()
        resultado = self.diccionario_posible_busqueda(buscar)
        self.lee_tabla_busqueda(datos=resultado)

    def boton_insertar_busqueda(self):
        ''' Se encarga de insertar en los entries de ciudad y departamento lo que fue encontrado 
            en la tabla'''
        try:
            # Carga los campos desde la tabla TreeView
            seleccion = self.tabla_busqueda.selection()
            items = self.tabla_busqueda.item(seleccion[len(seleccion)-1])
            valores = items['values']
            texto_departamento = valores[1]
            texto_ciudad = valores[2]
            self.insertar_texto_entry(self.entry_ciudad,texto_ciudad)
            self.insertar_texto_entry(self.entry_departamento,texto_departamento)
        except IndexError as error:
            mssg.showerror("¡ Atención !",'Por favor seleccione un ítem de la tabla')
            return

    def boton_grabar_ciudad(self):
        ''' Se encarga de pasar la entrada de la ciudad en la ventana emergente de Buscar Ciudad a la
            ventana de Inscripcion'''
        self.entry_ciudad.configure(state="normal")
        texto_ciudad = self.entry_ciudad.get()
        self.entry_ciudad.configure(state="readonly")
        if texto_ciudad not in (""," "):
            if mssg.askyesno("Grabar Ciudad",f"Esta Seguro Que Quiere Grabar La Ciudad: '{texto_ciudad}' En La Ventana De Inscripcion?"):
                self.insertar_texto_entry(entry=self.entries_inscripcion["Ciudad"],texto=texto_ciudad)
                self.win_busqueda.destroy()
                self.win_busqueda.update()
        else:
            mssg.showerror("Ciudad No Especificada","La Ciudad Que Se Quiere Grabar A La Seccion De Inscripcion No Ha Sido Especificada")

    def insertar_texto_entry(self,entry:tk.Entry,texto:str):
        '''Rutina Para Cambiar El Texto De Un Entry Que Por Defecto Es Readonly'''
        entry.configure(state="normal")
        entry.delete(0,tk.END)
        entry.insert(0,texto)
        entry.configure(state="readonly")

    def lee_tabla_busqueda(self,datos:dict=None):
        ''' Carga los datos de la BD y Limpia la Tabla De Ciudades, acepta parametro de Diccionario en caso tal
            de que se quiera cargar la tabla con respecto a un diccionario establecido, este diccionario es por ejemplo
            el diccionario de retorno de la funcion diccionario_posible_busqueda'''
        tabla_treeView = self.tabla_busqueda.get_children()
        for linea in tabla_treeView:
            self.tabla_busqueda.delete(linea) #Limpia los datos que habian antes del treeview
        # Seleccionando los datos de la BD
        if datos == None:
            query = 'SELECT * FROM t_ciudades ORDER BY Id_Ciudad DESC'
            db_rows = self.run_query(query)
            # Insertando los datos de la BD en la tabla de la pantalla
            self.diccionario_tabla_ciudades = {}
            for row in db_rows:
                id_departamento = str(row[0])
                id_ciudad = str(row[1])
                departamento = row[2]
                ciudad = row[3]
                self.tabla_busqueda.insert('',0, text = id_departamento, values = [id_ciudad,departamento,ciudad]) # db_rows = ["id_departamento","id_ciudad","departamento","ciudad"]
                self.diccionario_tabla_ciudades[id_ciudad] = {"Id_Departamento":id_departamento,"Departamento":departamento,"Ciudad":ciudad}
        else:
            for id_ciudad, info in datos.items():
                id_departamento = info["Id_Departamento"]
                departamento = info["Departamento"]
                ciudad = info["Ciudad"]
                self.tabla_busqueda.insert('',0, text = id_departamento, values = [id_ciudad,departamento,ciudad])


if __name__ == "__main__":
    app = Participantes()
    app.run()