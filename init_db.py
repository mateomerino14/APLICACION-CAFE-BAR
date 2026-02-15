import sqlite3
import os
import sys

#CREACION DE TRIGGER Y ESTRUCTURA DE LA BASE DE DATOS

def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    
    return os.path.join(base_path, 'database', 'cafebar.db')

DB_PATH = get_db_path()

def crear_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    tablaIngredientesStock = """CREATE TABLE IF NOT EXISTS Stock(
                              idIng INTEGER PRIMARY KEY AUTOINCREMENT,
                              nomIng VARCHAR(30) NOT NULL,
                              descripcion TEXT,
                              cantidadStock DECIMAL(10,2) DEFAULT 0.00,
                              disponible BOOLEAN DEFAULT TRUE,
                              unidadMedida VARCHAR(10) NOT NULL)"""
    
    tablaProductos = """CREATE TABLE IF NOT EXISTS Producto(
                      idProd INTEGER PRIMARY KEY AUTOINCREMENT,
                      nomProd VARCHAR(30) NOT NULL,
                      descripcion TEXT,
                      precioVenta DECIMAL(10,2) NOT NULL,
                      costoFabricacion DECIMAL(10,2) NOT NULL,
                      activo BOOLEAN DEFAULT TRUE,
                      imgProd BLOB NOT NULL,
                      idSubcategoria INTEGER NOT NULL,
                      FOREIGN KEY (idSubcategoria) REFERENCES Subcategoria(idSubcategoria))"""
    
    tablaCategoria = """CREATE TABLE IF NOT EXISTS Categoria(
                      idCategoria INTEGER PRIMARY KEY AUTOINCREMENT,
                      nomCategoria VARCHAR(30) UNIQUE NOT NULL,
                      imagenCategoria  BLOB NOT NULL, 
                      activa BOOLEAN DEFAULT TRUE)"""
    
    tablaSubcategoria = """CREATE TABLE IF NOT EXISTS Subcategoria(
                         idSubcategoria INTEGER PRIMARY KEY AUTOINCREMENT,
                         idCategoria INTEGER NOT NULL,
                         imagenSubcategoria BLOB NOT NULL, 
                         nombre VARCHAR(50) NOT NULL,
                         activa BOOLEAN DEFAULT TRUE,
                         FOREIGN KEY (idCategoria) REFERENCES Categoria(idCategoria)
                      )"""
    
    tablaProductosIngredientes = """CREATE TABLE IF NOT EXISTS ProductosIngredientes(
                                  idProd INTEGER NOT NULL,
                                  idIng INTEGER NOT NULL,
                                  cantidadIngNecesitada DECIMAL(10,2) NOT NULL,
                                  PRIMARY KEY(idProd,idIng),
                                  FOREIGN KEY (idProd) REFERENCES Producto(idProd),
                                  FOREIGN KEY (idIng) REFERENCES Stock(idIng))"""
                                  
    tablaMesas = """CREATE TABLE IF NOT EXISTS Mesa(
                  idMesa INTEGER,
                  disponible BOOLEAN DEFAULT TRUE,
                  existe BOOLEAN DEFAULT TRUE,
                  idSeccion INTEGER NOT NULL,
                  PRIMARY KEY (idMesa,idSeccion),
                  FOREIGN KEY (idSeccion) REFERENCES Seccion(idSeccion))"""
    
    tablaSecciones = """CREATE TABLE IF NOT EXISTS Seccion(
                      idSeccion INTEGER PRIMARY KEY AUTOINCREMENT,
                      nombSeccion VARCHAR(30) NOT NULL,
                      descripcion TEXT)"""
    
    tablaCliente = """CREATE TABLE IF NOT EXISTS Cliente(
                    nit INTEGER PRIMARY KEY,
                    nombCli VARCHAR(20) NOT NULL,
                    apellPatCli VARCHAR(30) NOT NULL,
                    apellMatCli VARCHAR(30) NOT NULL,
                    correoElCli VARCHAR(40) NOT NULL,
                    habilitado BOOLEAN DEFAULT TRUE)"""
    
    tablaImpresora = """CREATE TABLE IF NOT EXISTS Impresora (
                        idImpresora INTEGER PRIMARY KEY AUTOINCREMENT,
                        idVendor INTEGER,
                        idProducto INTEGER,
                        dispositivo TEXT,
                        descripcion TEXT,
                        es_barra BOOLEAN DEFAULT 0,
                        es_cocina BOOLEAN DEFAULT 0
                    );"""
    
    tablaPantallas = """CREATE TABLE IF NOT EXISTS Pantalla(
                      idPant INTEGER PRIMARY KEY AUTOINCREMENT,
                      nomPant VARCHAR(40) NOT NULL)"""
    
    tablaCargos = """CREATE TABLE IF NOT EXISTS Cargo(
                   idCargo INTEGER PRIMARY KEY AUTOINCREMENT,
                   nomCarg VARCHAR(20) UNIQUE NOT NULL)"""
    
    tablaPermisosCargos = """CREATE TABLE IF NOT EXISTS PermisosCargo(
                           idCarg INTEGER,
                           idPant INTEGER,
                           PRIMARY KEY(idCarg,idPant),
                           FOREIGN KEY (idCarg) REFERENCES Cargo(idCarg),
                           FOREIGN KEY (idPant) REFERENCES Pantalla(idPant))"""
    
    tablaEmpleado = """CREATE TABLE IF NOT EXISTS Empleado(
                     codEmp INTEGER PRIMARY KEY AUTOINCREMENT,
                     aliasEmp VARCHAR(30) NOT NULL,
                     contEmp VARCHAR(30) NOT NULL,
                     ciEmp INTEGER NOT NULL,
                     nomEmp VARCHAR(30) NOT NULL,
                     apellPatEmp VARCHAR(30) NOT NULL,
                     apellMatEmp VARCHAR(30) NOT NULL,
                     numCelEmp INTEGER NOT NULL,
                     direccionEmp VARCHAR(30) NOT NULL,
                     correoElEmp VARCHAR(30),
                     disponibleEmp BOOLEAN DEFAULT TRUE,
                     idCargo INTEGER NOT NULL,
                     imgEmp BLOB NOT NULL,
                     FOREIGN KEY (idCargo) REFERENCES Cargo(idCargo))"""
    
    tablaPermisosPersonal = """CREATE TABLE IF NOT EXISTS PermisosPersonal(
                             codEmp INTEGER NOT NULL,
                             idPant INTEGER NOT NULL,
                             PRIMARY KEY(codEmp,idPant),
                             FOREIGN KEY (codEmp) REFERENCES Empleado(codEmp),
                             FOREIGN KEY (idPant) REFERENCES Pantalla(idPant))"""
    
    tablaPromociones = """CREATE TABLE IF NOT EXISTS Promocion(
                            idProm INTEGER PRIMARY KEY AUTOINCREMENT,
                            nomProm VARCHAR(30) NOT NULL,
                            precioProm DECIMAL(10,2) NOT NULL,
                            imgProm BLOB NOT NULL,
                            activo BOOLEAN DEFAULT TRUE,
                            fechaEspecifica DATE,
                            fechaInicio DATE,
                            fechaFin DATE,
                            horaInicio TIME DEFAULT '00:00:00',
                            horaFin TIME DEFAULT '23:59:59')
                            """
    tablaDiasPromocion = """CREATE TABLE IF NOT EXISTS PromocionDias(
                       idProm INTEGER NOT NULL,
                       diaSemana INTEGER NOT NULL, 
                       PRIMARY KEY(idProm, diaSemana),
                       FOREIGN KEY (idProm) REFERENCES Promocion(idProm))"""
    
    tablaPromocionProductos = """CREATE TABLE IF NOT EXISTS PromocionProd(
                               idProm INTEGER NOT NULL,
                               idProd INTEGER NOT NULL,
                               cantidadProdProm INTEGER NOT NULL,
                               PRIMARY KEY (idProm,idProd),
                               FOREIGN KEY (idProm) REFERENCES Promocion(idProm),
                               FOREIGN KEY (idProd) REFERENCES Producto(idProd))"""
    
    tablaVenta = """CREATE TABLE IF NOT EXISTS Venta(
                  numVenta INTEGER NOT NULL,
                  fechaReg TEXT DEFAULT (DATETIME('now','localtime')),
                  horaReg TIME NOT NULL DEFAULT (CURRENT_TIME),
                  codEmp INTEGER NOT NULL,
                  codEmp2 INTEGER NOT NULL,
                  totalVenta DECIMAL(10,2) NOT NULL,
                  idMesa INTEGER,
                  idSeccion INTEGER,
                  nit INTEGER DEFAULT -1,
                  PRIMARY KEY(numVenta, fechaReg),
                  FOREIGN KEY(nit) REFERENCES Cliente(nit),
                  FOREIGN KEY (idMesa) REFERENCES Mesa(idMesa),
                  FOREIGN KEY (idSeccion) REFERENCES Seccion(idSeccion),
                  FOREIGN KEY (codEmp) REFERENCES Empleado(codEmp),
                  FOREIGN KEY (codEmp2) REFERENCES Empleado(codEmp)
                 )"""
    
    tablaMetodosPago = """CREATE TABLE IF NOT EXISTS MetodoPago(
                        idMetodo INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre VARCHAR(50) NOT NULL)"""
    
    tablaPago = """CREATE TABLE IF NOT EXISTS Pago(
                 numVenta INT NOT NULL,
                 fechaRegVenta TEXT DEFAULT (DATETIME('now','localtime')),
                 idMetodo INT NOT NULL,
                 monto DECIMAL(10, 2) NOT NULL,
                 PRIMARY KEY(numVenta, fechaRegVenta, idMetodo), 
                 FOREIGN KEY (numVenta, fechaRegVenta) REFERENCES Venta(numVenta, fechaReg),
                 FOREIGN KEY (idMetodo) REFERENCES MetodoPago(idMetodo))"""
    
    tablaDetallesVenta = """CREATE TABLE IF NOT EXISTS DetallesVenta(
                          idDetalleVenta INTEGER PRIMARY KEY AUTOINCREMENT,
                          numVenta INTEGER NOT NULL,
                          fechaRegVenta TEXT DEFAULT (DATETIME('now','localtime')),
                          fechaRegDetalleVenta TEXT DEFAULT (DATETIME('now','localtime')),
                          idProd INTEGER ,
                          idProm INTEGER ,
                          subtotal DECIMAL(10,2) NOT NULL,
                          cantidadProdDet INTEGER NOT NULL,
                          tipoConsumo VARCHAR(20) NOT NULL,
                          estadoDetalleVenta VARCHAR(20) NOT NULL DEFAULT FALSE,  
                          marcado BOOLEAN DEFAULT FALSE,
                          cantidadMarcado INTEGER DEFAULT 0,
                          idMeseroActual INTEGER NOT NULL,
                          FOREIGN KEY (numVenta,fechaRegVenta) REFERENCES Venta(numVenta,fechaReg),
                          FOREIGN KEY (idProd) REFERENCES Producto(idProd),
                          FOREIGN KEY (idMeseroActual) REFERENCES Empleado(codEmp)
                          FOREIGN KEY (idProm) REFERENCES Promocion(idProm)
                          )"""
    
    tablaDirectorio = """CREATE TABLE IF NOT EXISTS Directorio(
                       idAmin INTEGER PRIMARY KEY AUTOINCREMENT,
                       nomAdmin VARCHAR(30) NOT NULL,
                       contrasenaAdmin VARCHAR(30) NOT NULL)"""
    
    tablaCorreos = """CREATE TABLE IF NOT EXISTS Cuenta(
                    idCuenta INTEGER PRIMARY KEY AUTOINCREMENT,
                    activaCuenta BOOLEAN DEFAULT FALSE,
                    correoCuenta VARCHAR NOT NULL,
                    contCuenta VARCHAR NOT NULL)"""
    
  
    tablaEnlace = """CREATE TABLE IF NOT EXISTS Enlace(
                    idEnlace INTEGER PRIMARY KEY AUTOINCREMENT,
                    enlace VARCHAR(100) NOT NULL DEFAULT 'https://siat.impuestos.gob.bo/v2/launcher/'
                )"""
    
    c.executescript(tablaIngredientesStock)
    c.executescript(tablaCategoria)
    c.executescript(tablaSubcategoria)
    c.executescript(tablaProductos)
    c.executescript(tablaProductosIngredientes)
    c.executescript(tablaMesas)
    c.executescript(tablaSecciones)
    c.executescript(tablaCliente)
    c.executescript(tablaPantallas)
    c.executescript(tablaCargos)
    c.executescript(tablaPermisosCargos)
    c.executescript(tablaEmpleado)
    c.executescript(tablaPermisosPersonal)
    c.executescript(tablaPromociones)
    c.executescript(tablaDiasPromocion)
    c.executescript(tablaPromocionProductos)
    c.executescript(tablaVenta)
    c.executescript(tablaMetodosPago)
    c.executescript(tablaPago)
    c.executescript(tablaDetallesVenta)
    c.executescript(tablaDirectorio)
    c.executescript(tablaCorreos)
    c.executescript(tablaEnlace)
    c.executescript(tablaImpresora)
    #('Clientes'),
    consultaPaginas = """INSERT INTO Pantalla(nomPant) VALUES 
                        ('Familia'),
                        ('Caja'),
                        ('Administracion'),
                        ('Productos'),
                        ('Secciones'),
                        ('Stock'),
                        ('Promociones'),
                        ('Empleados'),
                        ('Reportes')"""
    consultaMetodosPago = """INSERT INTO MetodoPago(nombre) VALUES ('Efectivo')"""
    consultaMetodosPago2 = """INSERT INTO MetodoPago(nombre) VALUES ('Qr')"""
    
    c.execute("SELECT COUNT(*) FROM Pantalla")
    count = c.fetchone()[0]
    if count == 0:
        c.execute(consultaPaginas)
        
    c.execute("SELECT COUNT(*) FROM MetodoPago")
    count = c.fetchone()[0]
    if count == 0:
        c.execute(consultaMetodosPago)
        c.execute(consultaMetodosPago2)
    try:
        c.execute("SELECT COUNT(*) FROM Enlace")
        count = c.fetchone()[0]
        if count == 0:
            c.execute("INSERT INTO Enlace (enlace) VALUES (?)", 
                     ("https://siat.impuestos.gob.bo/v2/launcher/",))
    except Exception as e:
        print(f"Error al insertar enlace por defecto: {e}")

    try:
        c.execute("SELECT COUNT(*) FROM Directorio")
        count = c.fetchone()[0]
        if count == 0:
            ingresarAdmin = """INSERT INTO Directorio(nomAdmin,contrasenaAdmin) VALUES(?,?)"""
            c.execute(ingresarAdmin, ("DIRECTORIO", "79213966482250"))
    except Exception as e:
        print(f"Error al insertar directorio por defecto: {e}")
    conn.commit()
    conn.close()

def crearTriggers():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    triggerMesa = """
    CREATE TRIGGER IF NOT EXISTS asignarMesa
    AFTER INSERT ON Mesa
    FOR EACH ROW
    WHEN NEW.idMesa IS NULL
    BEGIN
        UPDATE Mesa
        SET idMesa = (
            SELECT COALESCE(MAX(idMesa),0)+1
            FROM Mesa
            WHERE idSeccion = NEW.idSeccion
              AND rowid != NEW.rowid
        )
        WHERE rowid = NEW.rowid;
    END;
    """

    c.executescript(triggerMesa)
    conn.commit()
    conn.close()

def inciarBaseDatos():
    crear_db()
    crearTriggers()
    
if __name__ == "__main__":
    inciarBaseDatos()
