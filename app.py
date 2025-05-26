from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necesario para usar sesiones

# Lista de productos de ejemplo
productos = [
    {
        'id': 1,
        'nombre': 'Lapiceros de Colores',
        'descripcion': 'Lapiceros de colores brillantes, ideales para dibujar y colorear.',
        'precio': 0.25,
        'imagen': 'lapiceros.jpg',
        'cantidad': 24
    },
    {
        'id': 2,
        'nombre': 'Folder Rojo',
        'descripcion': 'Folder color rojo, tamaño carta, ideal para organizar documentos.',
        'precio': 12.00,
        'imagen': 'folder rojo.jpg',
        'cantidad': 15
    },
    {
        'id': 3,
        'nombre': 'Folder Amarillo',
        'descripcion': 'Folder color amarillo, tamaño carta, ideal para organizar documentos.',
        'precio': 12.00,
        'imagen': 'folder amarillo.jpg',
        'cantidad': 15
    },
    {
        'id': 4,
        'nombre': 'Pega 60ml',
        'descripcion': 'Pegamento multiusos de 60ml, ideal para manualidades y oficina.',
        'precio': 35.00,
        'imagen': 'Pega 60ml.jpg',
        'cantidad': 30
    },
    # Puedes agregar más productos aquí
]

@app.route('/')
def index():
    return render_template('index.html', productos=productos)

@app.route('/ordenar', methods=['POST'])
def ordenar():
    producto_id = int(request.form['producto_id'])
    cantidad = int(request.form['cantidad'])
    producto = next((p for p in productos if p['id'] == producto_id), None)
    if producto:
        mensaje = f"Hola, quiero ordenar {cantidad} x {producto['nombre']} (ID: {producto['id']}) por ${producto['precio']} cada uno."
        # Redirige a WhatsApp con el mensaje
        return redirect(f"https://wa.me/?text={mensaje}")
    return redirect('/')

@app.route('/agregar_carrito', methods=['POST'])
def agregar_carrito():
    producto_id = int(request.form['producto_id'])
    cantidad = int(request.form['cantidad'])
    producto = next((p for p in productos if p['id'] == producto_id), None)
    if producto and cantidad > 0 and producto['cantidad'] >= cantidad:
        carrito = session.get('carrito', {})
        if str(producto_id) in carrito:
            if producto['cantidad'] >= carrito[str(producto_id)] + cantidad:
                carrito[str(producto_id)] += cantidad
        else:
            carrito[str(producto_id)] = cantidad
        session['carrito'] = carrito
        producto['cantidad'] -= cantidad
    return redirect(url_for('index'))

@app.route('/carrito')
def ver_carrito():
    carrito = session.get('carrito', {})
    items = []
    total = 0
    for pid, cantidad in carrito.items():
        prod = next((p for p in productos if p['id'] == int(pid)), None)
        if prod:
            subtotal = prod['precio'] * cantidad
            total += subtotal
            items.append({
                'id': prod['id'],
                'nombre': prod['nombre'],
                'precio': prod['precio'],
                'cantidad': cantidad,
                'subtotal': subtotal
            })
    return render_template('carrito.html', items=items, total=total)

@app.route('/enviar_pedido', methods=['GET', 'POST'])
def enviar_pedido():
    if request.method == 'POST':
        carrito = session.get('carrito', {})
        nombre_cliente = request.form.get('nombre_cliente', '').strip()
        mensaje = f'Hola, mi nombre es {nombre_cliente} y quiero pedir lo siguiente:%0A'
        for pid, cantidad in carrito.items():
            prod = next((p for p in productos if p['id'] == int(pid)), None)
            if prod:
                mensaje += f"- {cantidad} x {prod['nombre']} (${prod['precio']} c/u)%0A"
        mensaje += f"Total: ${sum(prod['precio']*cantidad for pid, cantidad in carrito.items() for prod in productos if prod['id']==int(pid))}"
        # Limpia el carrito después de enviar
        session['carrito'] = {}
        return redirect(f"https://wa.me/50379468807?text={mensaje}")
    else:
        return redirect(url_for('ver_carrito'))

@app.route('/eliminar_del_carrito', methods=['POST'])
def eliminar_del_carrito():
    producto_id = str(request.form['producto_id'])
    carrito = session.get('carrito', {})
    if producto_id in carrito:
        cantidad_devuelta = carrito[producto_id]
        prod = next((p for p in productos if p['id'] == int(producto_id)), None)
        if prod:
            prod['cantidad'] += cantidad_devuelta
        del carrito[producto_id]
        session['carrito'] = carrito
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
