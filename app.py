from flask import Flask, render_template, request, redirect
print(">>> APP ACTUALIZADO <<<")
import pymysql
import config

app = Flask(__name__)

# =====================================
# CONEXIÓN A MYSQL
# =====================================

def get_connection():
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

# =====================================
# DASHBOARD PRINCIPAL
# =====================================

@app.route('/')
def dashboard():

    conexion = get_connection()

    with conexion.cursor() as cursor:

        cursor.execute(
            "SELECT COUNT(*) total FROM productos"
        )
        productos = cursor.fetchone()['total']

        cursor.execute(
            "SELECT COUNT(*) total FROM clientes"
        )
        clientes = cursor.fetchone()['total']

        cursor.execute(
            "SELECT COUNT(*) total FROM proveedores"
        )
        proveedores = cursor.fetchone()['total']

        cursor.execute(
            "SELECT COUNT(*) total FROM ventas"
        )
        ventas = cursor.fetchone()['total']

        cursor.execute("""
            SELECT *
            FROM productos
            WHERE stock_actual <= stock_minimo
        """)

        stock_bajo = cursor.fetchall()

    conexion.close()

    return render_template(
        'dashboard.html',
        productos=productos,
        clientes=clientes,
        proveedores=proveedores,
        ventas=ventas,
        stock_bajo=stock_bajo
    )
# =====================================
# LISTAR PRODUCTOS
# =====================================

@app.route('/productos')
def productos():

    busqueda = request.args.get('busqueda', '')

    conexion = get_connection()

    with conexion.cursor() as cursor:

        sql = """
        SELECT *
        FROM productos
        WHERE activo = 1
        AND (
            nombre LIKE %s
            OR codigo LIKE %s
            OR marca LIKE %s
            OR categoria LIKE %s
            OR color LIKE %s
        )
        ORDER BY id_producto DESC
        """

        cursor.execute(
            sql,
            (
                f"%{busqueda}%",
                f"%{busqueda}%",
                f"%{busqueda}%",
                f"%{busqueda}%",
                f"%{busqueda}%"
            )
        )

        productos = cursor.fetchall()

    conexion.close()

    return render_template(
        'productos.html',
        productos=productos,
        busqueda=busqueda
    )

@app.route('/productos/nuevo')
def nuevo_producto():
    return render_template('nuevo_producto.html')

@app.route('/productos/guardar', methods=['POST'])
def guardar_producto():

    codigo = request.form['codigo']
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    marca = request.form['marca']
    categoria = request.form['categoria']
    color = request.form['color']
    precio_compra = request.form['precio_compra']
    precio_venta = request.form['precio_venta']
    stock_actual = request.form['stock_actual']

    conexion = get_connection()

    with conexion.cursor() as cursor:

        sql = """
        INSERT INTO productos
        (
            codigo,
            nombre,
            descripcion,
            marca,
            categoria,
            color,
            precio_compra,
            precio_venta,
            stock_actual,
            stock_minimo
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,5)
        """

        cursor.execute(
            sql,
            (
                codigo,
                nombre,
                descripcion,
                marca,
                categoria,
                color,
                precio_compra,
                precio_venta,
                stock_actual
            )
        )

    conexion.commit()
    conexion.close()

    return redirect('/productos')
@app.route('/productos/editar/<int:id>')
def editar_producto(id):

    conexion = get_connection()

    with conexion.cursor() as cursor:

        cursor.execute(
            "SELECT * FROM productos WHERE id_producto = %s",
            (id,)
        )

        producto = cursor.fetchone()

    conexion.close()

    return render_template(
        'editar_producto.html',
        producto=producto
    )

@app.route('/productos/actualizar', methods=['POST'])
def actualizar_producto():

    id_producto = request.form['id_producto']
    codigo = request.form['codigo']
    nombre = request.form['nombre']
    marca = request.form['marca']
    precio_compra = request.form['precio_compra']
    precio_venta = request.form['precio_venta']
    stock_actual = request.form['stock_actual']

    conexion = get_connection()

    with conexion.cursor() as cursor:

        sql = """
        UPDATE productos
        SET
            codigo=%s,
            nombre=%s,
            marca=%s,
            precio_compra=%s,
            precio_venta=%s,
            stock_actual=%s
        WHERE id_producto=%s
        """

        cursor.execute(
            sql,
            (
                codigo,
                nombre,
                marca,
                precio_compra,
                precio_venta,
                stock_actual,
                id_producto
            )
        )

    conexion.commit()
    conexion.close()

    return redirect('/productos')

@app.route('/productos/eliminar/<int:id>')
def eliminar_producto(id):

    conexion = get_connection()

    with conexion.cursor() as cursor:

        cursor.execute("""
            UPDATE productos
            SET activo = 0
            WHERE id_producto = %s
        """, (id,))

    conexion.commit()
    conexion.close()

    return redirect('/productos')
@app.route('/proveedores')
def proveedores():

    busqueda = request.args.get('busqueda', '')

    conexion = get_connection()

    with conexion.cursor() as cursor:

        cursor.execute(
            """
            SELECT *
            FROM proveedores
            WHERE nombre LIKE %s
               OR telefono LIKE %s
               OR correo LIKE %s
            """,
            (
                f"%{busqueda}%",
                f"%{busqueda}%",
                f"%{busqueda}%"
            )
        )

        proveedores = cursor.fetchall()

    conexion.close()

    return render_template(
        'proveedores.html',
        proveedores=proveedores,
        busqueda=busqueda
    )

@app.route('/proveedores/nuevo')
def nuevo_proveedor():
    return render_template(
        'nuevo_proveedor.html'
    )

@app.route('/proveedores/guardar', methods=['POST'])
def guardar_proveedor():

    nombre = request.form['nombre']
    telefono = request.form['telefono']
    correo = request.form['correo']
    direccion = request.form['direccion']

    conexion = get_connection()

    with conexion.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO proveedores
            (
                nombre,
                telefono,
                correo,
                direccion
            )
            VALUES
            (%s,%s,%s,%s)
            """,
            (
                nombre,
                telefono,
                correo,
                direccion
            )
        )

    conexion.commit()
    conexion.close()

    return redirect('/proveedores')

@app.route('/proveedores/editar/<int:id>')
def editar_proveedor(id):

    conexion = get_connection()

    with conexion.cursor() as cursor:

        cursor.execute(
            "SELECT * FROM proveedores WHERE id_proveedor = %s",
            (id,)
        )

        proveedor = cursor.fetchone()

    conexion.close()

    return render_template(
        'editar_proveedor.html',
        proveedor=proveedor
    )

@app.route('/proveedores/actualizar', methods=['POST'])
def actualizar_proveedor():

    id_proveedor = request.form['id_proveedor']
    nombre = request.form['nombre']
    telefono = request.form['telefono']
    correo = request.form['correo']
    direccion = request.form['direccion']

    conexion = get_connection()

    with conexion.cursor() as cursor:

        cursor.execute(
            """
            UPDATE proveedores
            SET
                nombre=%s,
                telefono=%s,
                correo=%s,
                direccion=%s
            WHERE id_proveedor=%s
            """,
            (
                nombre,
                telefono,
                correo,
                direccion,
                id_proveedor
            )
        )

    conexion.commit()
    conexion.close()

    return redirect('/proveedores')

@app.route('/proveedores/eliminar/<int:id>')
def eliminar_proveedor(id):

    conexion = get_connection()

    with conexion.cursor() as cursor:

        cursor.execute(
            "DELETE FROM proveedores WHERE id_proveedor = %s",
            (id,)
        )

    conexion.commit()
    conexion.close()

    return redirect('/proveedores')
@app.route('/compras')
def compras():

    busqueda = request.args.get('busqueda', '')

    conexion = get_connection()

    with conexion.cursor() as cursor:

        cursor.execute("""
        SELECT
            c.id_compra,
            c.fecha,
            c.total,
            p.nombre AS proveedor
        FROM compras c
        INNER JOIN proveedores p
            ON c.id_proveedor = p.id_proveedor
        WHERE p.nombre LIKE %s
        ORDER BY c.id_compra DESC
        """,
        (f"%{busqueda}%",))

        compras = cursor.fetchall()

    conexion.close()

    return render_template(
        'compras.html',
        compras=compras,
        busqueda=busqueda
    )

@app.route('/compras/nueva')
def nueva_compra():

    conexion = get_connection()

    with conexion.cursor() as cursor:

        cursor.execute(
            "SELECT * FROM proveedores"
        )
        proveedores = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM productos"
        )
        productos = cursor.fetchall()

    conexion.close()

    return render_template(
        'nueva_compra.html',
        proveedores=proveedores,
        productos=productos
    )

@app.route('/compras/guardar', methods=['POST'])
def guardar_compra():

    id_proveedor = request.form['id_proveedor']
    id_producto = request.form['id_producto']

    cantidad = int(
        request.form['cantidad']
    )

    precio_unitario = float(
        request.form['precio_unitario']
    )

    total = cantidad * precio_unitario

    conexion = get_connection()

    with conexion.cursor() as cursor:

        # Registrar compra

        cursor.execute("""
        INSERT INTO compras
        (
            total,
            id_proveedor,
            id_usuario
        )
        VALUES
        (%s,%s,1)
        """,
        (
            total,
            id_proveedor
        ))

        id_compra = cursor.lastrowid

        # Detalle compra

        cursor.execute("""
        INSERT INTO detalle_compras
        (
            id_compra,
            id_producto,
            cantidad,
            precio_unitario,
            subtotal
        )
        VALUES
        (%s,%s,%s,%s,%s)
        """,
        (
            id_compra,
            id_producto,
            cantidad,
            precio_unitario,
            total
        ))

        # Actualizar stock

        cursor.execute("""
        UPDATE productos
        SET stock_actual =
            stock_actual + %s
        WHERE id_producto = %s
        """,
        (
            cantidad,
            id_producto
        ))

    conexion.commit()
    conexion.close()

    return redirect('/compras')

@app.route('/ventas')
def ventas():

    busqueda = request.args.get('busqueda', '')

    conexion = get_connection()

    with conexion.cursor() as cursor:

        cursor.execute("""
        SELECT
            v.id_venta,
            v.fecha,
            v.total,
            c.nombre AS cliente
        FROM ventas v
        INNER JOIN clientes c
            ON v.id_cliente = c.id_cliente
        WHERE c.nombre LIKE %s
        ORDER BY v.id_venta DESC
        """,
        (f"%{busqueda}%",))

        ventas = cursor.fetchall()

    conexion.close()

    return render_template(
        'ventas.html',
        ventas=ventas,
        busqueda=busqueda
    )


@app.route('/ventas/nueva')
def nueva_venta():

    conexion = get_connection()

    with conexion.cursor() as cursor:

        cursor.execute(
            "SELECT * FROM productos"
        )

        productos = cursor.fetchall()

    conexion.close()

    return render_template(
        'nueva_venta.html',
        productos=productos
    )

@app.route('/ventas/guardar', methods=['POST'])
def guardar_venta():

    nombre_cliente = request.form['cliente']
    id_producto = request.form['id_producto']
    cantidad = int(request.form['cantidad'])

    conexion = get_connection()

    with conexion.cursor() as cursor:

        # Buscar cliente

        cursor.execute(
            "SELECT id_cliente FROM clientes WHERE nombre = %s",
            (nombre_cliente,)
        )

        cliente = cursor.fetchone()

        # Si no existe, crearlo

        if not cliente:

            cursor.execute(
                """
                INSERT INTO clientes (nombre)
                VALUES (%s)
                """,
                (nombre_cliente,)
            )

            id_cliente = cursor.lastrowid

        else:

            id_cliente = cliente['id_cliente']

        # Buscar producto

        cursor.execute(
            """
            SELECT precio_venta, stock_actual
            FROM productos
            WHERE id_producto = %s
            """,
            (id_producto,)
        )

        producto = cursor.fetchone()

        if cantidad > producto['stock_actual']:

            conexion.close()
            return "Stock insuficiente"

        precio = producto['precio_venta']
        total = cantidad * precio

        # Crear venta

        cursor.execute(
            """
            INSERT INTO ventas
            (
                total,
                id_cliente,
                id_usuario
            )
            VALUES
            (%s,%s,1)
            """,
            (total, id_cliente)
        )

        id_venta = cursor.lastrowid

        # Detalle venta

        cursor.execute(
            """
            INSERT INTO detalle_ventas
            (
                id_venta,
                id_producto,
                cantidad,
                precio_unitario,
                subtotal
            )
            VALUES
            (%s,%s,%s,%s,%s)
            """,
            (
                id_venta,
                id_producto,
                cantidad,
                precio,
                total
            )
        )

        # Descontar stock

        cursor.execute(
            """
            UPDATE productos
            SET stock_actual = stock_actual - %s
            WHERE id_producto = %s
            """,
            (
                cantidad,
                id_producto
            )
        )

    conexion.commit()
    conexion.close()

    return redirect('/ventas')

@app.route('/informes')
def informes():

    conexion = get_connection()
    cursor = conexion.cursor()

    # =====================================
    # INFORME DEL DÍA
    # =====================================

    cursor.execute("""
        SELECT COALESCE(SUM(total),0) AS total_ventas
        FROM ventas
        WHERE DATE(fecha)=CURDATE()
    """)
    ventas_hoy = cursor.fetchone()['total_ventas']

    cursor.execute("""
        SELECT COALESCE(SUM(total),0) AS total_compras
        FROM compras
        WHERE DATE(fecha)=CURDATE()
    """)
    gastos_hoy = cursor.fetchone()['total_compras']

    utilidad_hoy = ventas_hoy - gastos_hoy


    # =====================================
    # INFORME SEMANAL
    # =====================================

    cursor.execute("""
        SELECT COALESCE(SUM(total),0) AS total_ventas
        FROM ventas
        WHERE YEARWEEK(fecha,1)=YEARWEEK(CURDATE(),1)
    """)
    ventas_semana = cursor.fetchone()['total_ventas']

    cursor.execute("""
        SELECT COALESCE(SUM(total),0) AS total_compras
        FROM compras
        WHERE YEARWEEK(fecha,1)=YEARWEEK(CURDATE(),1)
    """)
    gastos_semana = cursor.fetchone()['total_compras']

    utilidad_semana = ventas_semana - gastos_semana


    # =====================================
    # INFORME MENSUAL
    # =====================================

    cursor.execute("""
        SELECT COALESCE(SUM(total),0) AS total_ventas
        FROM ventas
        WHERE MONTH(fecha)=MONTH(CURDATE())
          AND YEAR(fecha)=YEAR(CURDATE())
    """)
    ventas_mes = cursor.fetchone()['total_ventas']

    cursor.execute("""
        SELECT COALESCE(SUM(total),0) AS total_compras
        FROM compras
        WHERE MONTH(fecha)=MONTH(CURDATE())
          AND YEAR(fecha)=YEAR(CURDATE())
    """)
    gastos_mes = cursor.fetchone()['total_compras']

    utilidad_mes = ventas_mes - gastos_mes


    # =====================================
    # TOP 5 PRODUCTOS MÁS VENDIDOS
    # =====================================

    cursor.execute("""
        SELECT
            p.nombre,
            SUM(dv.cantidad) AS total_vendido
        FROM detalle_ventas dv
        INNER JOIN productos p
            ON dv.id_producto = p.id_producto
        GROUP BY p.id_producto, p.nombre
        ORDER BY total_vendido DESC
        LIMIT 5
    """)

    productos_mas_vendidos = cursor.fetchall()


    # =====================================
    # TOP 5 PROVEEDORES
    # =====================================

    cursor.execute("""
        SELECT
            pr.nombre,
            COUNT(c.id_compra) AS total_compras
        FROM compras c
        INNER JOIN proveedores pr
            ON c.id_proveedor = pr.id_proveedor
        GROUP BY pr.id_proveedor, pr.nombre
        ORDER BY total_compras DESC
        LIMIT 5
    """)

    proveedores_top = cursor.fetchall()


    # =====================================
    # PRODUCTOS CON STOCK BAJO
    # =====================================

    cursor.execute("""
        SELECT
            nombre,
            stock_actual,
            stock_minimo
        FROM productos
        WHERE stock_actual <= stock_minimo
        ORDER BY stock_actual ASC
    """)

    stock_bajo = cursor.fetchall()


    # =====================================
    # CERRAR CONEXIÓN
    # =====================================

    cursor.close()
    conexion.close()


    # =====================================
    # ENVIAR DATOS AL HTML
    # =====================================

    return render_template(
        'informes.html',

        ventas_hoy=ventas_hoy,
        gastos_hoy=gastos_hoy,
        utilidad_hoy=utilidad_hoy,

        ventas_semana=ventas_semana,
        gastos_semana=gastos_semana,
        utilidad_semana=utilidad_semana,

        ventas_mes=ventas_mes,
        gastos_mes=gastos_mes,
        utilidad_mes=utilidad_mes,

        productos_mas_vendidos=productos_mas_vendidos,
        proveedores_top=proveedores_top,
        stock_bajo=stock_bajo
    )
# =====================================
# INICIAR SERVIDOR
# =====================================

import threading
import webbrowser

def abrir_navegador():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    threading.Timer(1.5, abrir_navegador).start()

    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )

    
  