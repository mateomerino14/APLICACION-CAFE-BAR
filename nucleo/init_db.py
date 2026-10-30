import sqlite3
import os
from nucleo.Rutas import get_db_path

DB_PATH = get_db_path()


# Crea las tablas y carga los datos iniciales que falten
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
                              unidadMedida VARCHAR(10) NOT NULL,
                              precioExtra DECIMAL(10,2) DEFAULT 0.00)"""

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

    tablaSubpantalla = """CREATE TABLE IF NOT EXISTS Subpantalla(
                        idSubPant INTEGER PRIMARY KEY AUTOINCREMENT,
                        idPant INTEGER NOT NULL,
                        nomSubPant VARCHAR(50) NOT NULL,
                        accion VARCHAR(50) NOT NULL,
                        FOREIGN KEY (idPant) REFERENCES Pantalla(idPant))"""

    tablaCargos = """CREATE TABLE IF NOT EXISTS Cargo(
                   idCargo INTEGER PRIMARY KEY AUTOINCREMENT,
                   nomCarg VARCHAR(20) UNIQUE NOT NULL)"""

    tablaPermisosCargos = """CREATE TABLE IF NOT EXISTS PermisosCargo(
                           idCarg INTEGER,
                           idPant INTEGER,
                           PRIMARY KEY(idCarg,idPant),
                           FOREIGN KEY (idCarg) REFERENCES Cargo(idCarg),
                           FOREIGN KEY (idPant) REFERENCES Pantalla(idPant))"""

    tablaPermisosCargoSubpantalla = """CREATE TABLE IF NOT EXISTS PermisosCargoSubpantalla(
                                      idCarg INTEGER NOT NULL,
                                      idSubPant INTEGER NOT NULL,
                                      PRIMARY KEY(idCarg, idSubPant),
                                      FOREIGN KEY (idCarg) REFERENCES Cargo(idCarg),
                                      FOREIGN KEY (idSubPant) REFERENCES Subpantalla(idSubPant))"""

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

    tablaPermisosPersonalSubpantalla = """CREATE TABLE IF NOT EXISTS PermisosPersonalSubpantalla(
                                         codEmp INTEGER NOT NULL,
                                         idSubPant INTEGER NOT NULL,
                                         PRIMARY KEY(codEmp, idSubPant),
                                         FOREIGN KEY (codEmp) REFERENCES Empleado(codEmp),
                                         FOREIGN KEY (idSubPant) REFERENCES Subpantalla(idSubPant))"""

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
                  impresiones_ticket INTEGER DEFAULT 0,
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

    tablaDetallesVentaExclusiones = """CREATE TABLE IF NOT EXISTS DetallesVentaExclusiones(
                          idExclusion INTEGER PRIMARY KEY AUTOINCREMENT,
                          idDetalleVenta INTEGER NOT NULL,
                          idIng INTEGER NOT NULL,
                          nomIng VARCHAR(30) NOT NULL,
                          FOREIGN KEY (idDetalleVenta) REFERENCES DetallesVenta(idDetalleVenta),
                          FOREIGN KEY (idIng) REFERENCES Stock(idIng))"""

    tablaDetallesVentaExclusionesPromo = """CREATE TABLE IF NOT EXISTS DetallesVentaExclusionesPromo(
                          idExclusion INTEGER PRIMARY KEY AUTOINCREMENT,
                          idDetalleVenta INTEGER NOT NULL,
                          idProd INTEGER NOT NULL,
                          idIng INTEGER NOT NULL,
                          nomIng VARCHAR(30) NOT NULL,
                          FOREIGN KEY (idDetalleVenta) REFERENCES DetallesVenta(idDetalleVenta),
                          FOREIGN KEY (idProd) REFERENCES Producto(idProd),
                          FOREIGN KEY (idIng) REFERENCES Stock(idIng))"""

    tablaDetallesVentaExtras = """CREATE TABLE IF NOT EXISTS DetallesVentaExtras(
                          idExtra INTEGER PRIMARY KEY AUTOINCREMENT,
                          idDetalleVenta INTEGER NOT NULL,
                          idIng INTEGER NOT NULL,
                          nomIng VARCHAR(30) NOT NULL,
                          cantidadExtra DECIMAL(10,2) NOT NULL,
                          precioExtra DECIMAL(10,2) NOT NULL,
                          idProd INTEGER,
                          numUnidad INTEGER,
                          FOREIGN KEY (idDetalleVenta) REFERENCES DetallesVenta(idDetalleVenta),
                          FOREIGN KEY (idIng) REFERENCES Stock(idIng),
                          FOREIGN KEY (idProd) REFERENCES Producto(idProd))"""

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
    c.executescript(tablaSubpantalla)
    c.executescript(tablaCargos)
    c.executescript(tablaPermisosCargos)
    c.executescript(tablaPermisosCargoSubpantalla)
    c.executescript(tablaEmpleado)
    c.executescript(tablaPermisosPersonal)
    c.executescript(tablaPermisosPersonalSubpantalla)
    c.executescript(tablaPromociones)
    c.executescript(tablaDiasPromocion)
    c.executescript(tablaPromocionProductos)
    c.executescript(tablaVenta)
    c.executescript(tablaMetodosPago)
    c.executescript(tablaPago)
    c.executescript(tablaDetallesVenta)
    c.executescript(tablaDetallesVentaExclusiones)
    c.executescript(tablaDirectorio)
    c.executescript(tablaCorreos)
    c.executescript(tablaEnlace)
    c.executescript(tablaImpresora)
    c.executescript(tablaDetallesVentaExclusionesPromo)
    c.executescript(tablaDetallesVentaExtras)

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
        subpantallas = [
            (1, 'Familia', 'VER_FAMILIA'),
            (2, 'Registrar Pedido', 'REGISTRAR_PEDIDO'),
            (3, 'Configuración', 'CONFIGURACION'),
            (3, 'Impresoras', 'IMPRESORAS'),
            (4, 'Registrar Categoría', 'REGISTRAR_CATEGORIA'),
            (4, 'Modificar Categoría', 'MODIFICAR_CATEGORIA'),
            (4, 'Dar de Baja Categoría', 'BAJA_CATEGORIA'),
            (4, 'Registrar Producto', 'REGISTRAR_PRODUCTO'),
            (4, 'Modificar Producto', 'MODIFICAR_PRODUCTO'),
            (4, 'Dar de Baja Producto', 'BAJA_PRODUCTO'),
            (5, 'Administrar Secciones', 'ADMIN_SECCIONES'),
            (6, 'Registrar Ingredientes', 'REGISTRAR_INGREDIENTES'),
            (6, 'Modificar Ingredientes', 'MODIFICAR_INGREDIENTES'),
            (7, 'Registrar Promociones', 'REGISTRAR_PROMOCIONES'),
            (7, 'Modificar Promociones', 'MODIFICAR_PROMOCIONES'),
            (7, 'Dar de Baja Promociones', 'BAJA_PROMOCIONES'),
            (8, 'Registrar Cargos', 'REGISTRAR_CARGOS'),
            (8, 'Modificar Cargos', 'MODIFICAR_CARGOS'),
            (8, 'Registrar Empleados', 'REGISTRAR_EMPLEADOS'),
            (8, 'Modificar Empleados', 'MODIFICAR_EMPLEADOS'),
            (8, 'Dar de Baja Empleados', 'BAJA_EMPLEADOS'),
            (9, 'Ver Reportes', 'VER_REPORTES'),
        ]
        for id_pant, nombre, accion in subpantallas:
            c.execute(
                "INSERT INTO Subpantalla (idPant, nomSubPant, accion) VALUES (?, ?, ?)", (id_pant, nombre, accion)
            )

    c.execute("SELECT COUNT(*) FROM MetodoPago")
    count = c.fetchone()[0]
    if count == 0:
        c.execute(consultaMetodosPago)
        c.execute(consultaMetodosPago2)

    try:
        c.execute("SELECT COUNT(*) FROM Enlace")
        count = c.fetchone()[0]
        if count == 0:
            c.execute("INSERT INTO Enlace (enlace) VALUES (?)", ("https://siat.impuestos.gob.bo/v2/launcher/",))
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


# Crea el trigger que numera las mesas de cada sección
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


# Crea la tabla de ingredientes excluidos dentro de promociones
def migrarTablaExclusionesPromo():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS DetallesVentaExclusionesPromo(
                      idExclusion INTEGER PRIMARY KEY AUTOINCREMENT,
                      idDetalleVenta INTEGER NOT NULL,
                      idProd INTEGER NOT NULL,
                      idIng INTEGER NOT NULL,
                      nomIng VARCHAR(30) NOT NULL,
                      numUnidad INTEGER NOT NULL DEFAULT 0,
                      FOREIGN KEY (idDetalleVenta) REFERENCES DetallesVenta(idDetalleVenta),
                      FOREIGN KEY (idProd) REFERENCES Producto(idProd),
                      FOREIGN KEY (idIng) REFERENCES Stock(idIng))""")

        c.execute("""CREATE TABLE IF NOT EXISTS DetallesVentaUnidades(
                      idUnidad INTEGER PRIMARY KEY AUTOINCREMENT,
                      idDetalleVenta INTEGER NOT NULL,
                      numUnidad INTEGER NOT NULL,
                      marcado BOOLEAN DEFAULT FALSE,
                      FOREIGN KEY (idDetalleVenta) REFERENCES DetallesVenta(idDetalleVenta))""")
        try:
            c.execute("ALTER TABLE DetallesVentaExclusionesPromo ADD COLUMN numUnidad INTEGER NOT NULL DEFAULT 0")
        except Exception:
            pass
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error en migración: {e}")


# Crea la tabla de ingredientes excluidos en bases creadas antes de existir
def migrarTablaExclusiones():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS DetallesVentaExclusiones(
                      idExclusion INTEGER PRIMARY KEY AUTOINCREMENT,
                      idDetalleVenta INTEGER NOT NULL,
                      idIng INTEGER NOT NULL,
                      nomIng VARCHAR(30) NOT NULL,
                      FOREIGN KEY (idDetalleVenta) REFERENCES DetallesVenta(idDetalleVenta),
                      FOREIGN KEY (idIng) REFERENCES Stock(idIng))""")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error en migración de exclusiones: {e}")


# Relaciona cada unidad vendida con su producto
def migrar_unidades_con_producto():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE DetallesVentaUnidades ADD COLUMN idProd INTEGER")
        print("Columna idProd agregada a DetallesVentaUnidades")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("La columna idProd ya existe")
        else:
            raise
    c.execute("CREATE INDEX IF NOT EXISTS idx_unidades_idprod ON DetallesVentaUnidades(idProd)")
    c.execute("""
            UPDATE DetallesVentaUnidades 
            SET idProd = (
                SELECT idProd FROM DetallesVenta 
                WHERE DetallesVenta.idDetalleVenta = DetallesVentaUnidades.idDetalleVenta
            )
            WHERE idProd IS NULL AND idDetalleVenta IN (
                SELECT idDetalleVenta FROM DetallesVenta WHERE idProd IS NOT NULL
            )
        """)
    print(f"Actualizadas {c.rowcount} unidades de productos normales")
    conn.commit()
    conn.close()


# Agrega el precio extra de ingredientes y la tabla de extras por pedido
def migrarIngredientesExtra():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("ALTER TABLE Stock ADD COLUMN precioExtra DECIMAL(10,2) DEFAULT 0.00")
            print("Columna precioExtra agregada a Stock")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("La columna precioExtra ya existe en Stock")
            else:
                raise
        c.execute("""CREATE TABLE IF NOT EXISTS DetallesVentaExtras(
                      idExtra INTEGER PRIMARY KEY AUTOINCREMENT,
                      idDetalleVenta INTEGER NOT NULL,
                      idIng INTEGER NOT NULL,
                      nomIng VARCHAR(30) NOT NULL,
                      cantidadExtra DECIMAL(10,2) NOT NULL,
                      precioExtra DECIMAL(10,2) NOT NULL,
                      idProd INTEGER,
                      numUnidad INTEGER,
                      FOREIGN KEY (idDetalleVenta) REFERENCES DetallesVenta(idDetalleVenta),
                      FOREIGN KEY (idIng) REFERENCES Stock(idIng))""")
        # idProd y numUnidad quedan en NULL salvo que el extra sea de un producto dentro de una promoción
        try:
            c.execute("ALTER TABLE DetallesVentaExtras ADD COLUMN idProd INTEGER")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise
        try:
            c.execute("ALTER TABLE DetallesVentaExtras ADD COLUMN numUnidad INTEGER")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error en migración de ingredientes extra: {e}")


# Agrega la hora de cierre de la venta, que se llena al cobrarla
def migrarHoraCierreVenta():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("ALTER TABLE Venta ADD COLUMN horaCierre TEXT")
            print("Columna horaCierre agregada a Venta")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("La columna horaCierre ya existe en Venta")
            else:
                raise
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error en migración de horaCierre: {e}")


# Convierte a bcrypt las contraseñas que sigan en texto plano
def migrarPasswordsAHash():
    try:
        from nucleo.SeguridadUtils import hashear_password, es_hash_bcrypt
    except ImportError:
        print("ADVERTENCIA: no se encontró el paquete 'bcrypt' (o SeguridadUtils.py).")
        print("Instala bcrypt con: pip install bcrypt --break-system-packages")
        print("Las contraseñas seguirán en texto plano hasta que se instale.")
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT codEmp, contEmp FROM Empleado")
        empleados = c.fetchall()
        migrados_emp = 0
        for cod, cont in empleados:
            if cont and not es_hash_bcrypt(cont):
                nuevo_hash = hashear_password(cont)
                c.execute("UPDATE Empleado SET contEmp=? WHERE codEmp=?", (nuevo_hash, cod))
                migrados_emp += 1

        c.execute("SELECT idAmin, contrasenaAdmin FROM Directorio")
        admins = c.fetchall()
        migrados_admin = 0
        for id_admin, cont in admins:
            if cont and not es_hash_bcrypt(cont):
                nuevo_hash = hashear_password(cont)
                c.execute("UPDATE Directorio SET contrasenaAdmin=? WHERE idAmin=?", (nuevo_hash, id_admin))
                migrados_admin += 1

        conn.commit()
        conn.close()
        if migrados_emp or migrados_admin:
            print(
                f"Migración de contraseñas: {migrados_emp} empleado(s) y {migrados_admin} cuenta(s) de directorio hasheadas."
            )
    except Exception as e:
        print(f"Error en migración de contraseñas: {e}")


# Prepara la base al iniciar: tablas, triggers y migraciones pendientes
def inciarBaseDatos():
    crear_db()
    crearTriggers()
    migrarTablaExclusiones()
    migrarTablaExclusionesPromo()
    migrar_unidades_con_producto()
    migrarIngredientesExtra()
    migrarHoraCierreVenta()
    migrarPasswordsAHash()


if __name__ == "__main__":
    inciarBaseDatos()
