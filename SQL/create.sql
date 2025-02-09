CREATE TABLE t_participantes(
    Id INTEGER PRIMARY KEY UNIQUE NOT NULL,
    Nombre TEXT,
    Direccion TEXT,
    Celular INTEGER,
    Entidad TEXT,
    Fecha DATE(10)
);

CREATE TABLE t_ciudades(
    Id_Departamento INTEGER NOT NULL,
    Id_Ciudad INTEGER NOT NULL,
    Nombre_Departamento TEXT,
    Nombre_Ciudad TEXT,
    PRIMARY KEY(Id_Departamento,Id_Ciudad)
);