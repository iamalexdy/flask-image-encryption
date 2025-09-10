from flask import Flask, render_template, request, send_file, jsonify, send_from_directory, redirect, url_for
from PIL import Image
from cryptography.fernet import Fernet
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import os
import io
import numpy as np

app = Flask(__name__)

# === CIFRADO CON FERNET (AES) ===
key = Fernet.generate_key()
cipher = Fernet(key)

def encriptar_texto(texto):
    return cipher.encrypt(texto.encode())

def desencriptar_texto(texto_encriptado):
    return cipher.decrypt(texto_encriptado).decode()

def obtener_matriz_numerica(imagen_path):
    """Convierte la imagen en una matriz numérica (valores de 0-255 por píxel)."""
    imagen = Image.open(imagen_path).convert('L')
    return np.array(imagen).tolist()

def ocultar_texto(imagen_path, texto, output_path="imagen_oculta.png"):
    imagen = Image.open(imagen_path)
    if imagen.mode != 'RGB':
        imagen = imagen.convert('RGB')
    pixeles = imagen.load()

    texto_cifrado = encriptar_texto(texto)
    binario_texto = ''.join([format(byte, '08b') for byte in texto_cifrado])

    ancho, alto = imagen.size
    if len(binario_texto) > ancho * alto * 3:
        raise ValueError("El texto es demasiado largo para ocultarlo en la imagen.")

    index = 0
    for y in range(alto):
        for x in range(ancho):
            if index < len(binario_texto):
                r, g, b = pixeles[x, y]
                r = (r & ~1) | int(binario_texto[index])
                g = (g & ~1) | int(binario_texto[index + 1]) if index + 1 < len(binario_texto) else g
                b = (b & ~1) | int(binario_texto[index + 2]) if index + 2 < len(binario_texto) else b
                pixeles[x, y] = (r, g, b)
                index += 3
            else:
                break

    imagen.save(output_path)
    return output_path

def extraer_texto(imagen_path):
    imagen = Image.open(imagen_path)
    pixeles = imagen.load()
    ancho, alto = imagen.size
    binario_texto = []

    for y in range(alto):
        for x in range(ancho):
            r, g, b = pixeles[x, y]
            binario_texto.append(r & 1)
            binario_texto.append(g & 1)
            binario_texto.append(b & 1)

    byte_data = [int(''.join(map(str, binario_texto[i:i + 8])), 2) for i in range(0, len(binario_texto), 8)]
    try:
        texto_encriptado = bytes(byte_data)
        return desencriptar_texto(texto_encriptado)
    except Exception as e:
        return str(e)

# === CIFRADO CON 3DES ===
key_3des = DES3.adjust_key_parity(get_random_bytes(24))

def encriptar_texto_3des(texto):
    cipher = DES3.new(key_3des, DES3.MODE_ECB)
    texto_padded = pad(texto.encode(), DES3.block_size)
    texto_encriptado = cipher.encrypt(texto_padded)
    return base64.b64encode(texto_encriptado)

def desencriptar_texto_3des(texto_encriptado):
    cipher = DES3.new(key_3des, DES3.MODE_ECB)
    texto_encriptado = base64.b64decode(texto_encriptado)
    texto_descifrado = unpad(cipher.decrypt(texto_encriptado), DES3.block_size)
    return texto_descifrado.decode()

def ocultar_texto_3des(imagen_path, texto, output_path="imagen_oculta.png"):
    imagen = Image.open(imagen_path)
    if imagen.mode != 'RGB':
        imagen = imagen.convert('RGB')
    pixeles = imagen.load()

    texto_cifrado = encriptar_texto_3des(texto)
    binario_texto = ''.join([format(byte, '08b') for byte in texto_cifrado])

    ancho, alto = imagen.size
    if len(binario_texto) > ancho * alto * 3:
        raise ValueError("El texto es demasiado largo para ocultarlo en la imagen.")

    index = 0
    for y in range(alto):
        for x in range(ancho):
            if index < len(binario_texto):
                r, g, b = pixeles[x, y]
                r = (r & ~1) | int(binario_texto[index])
                g = (g & ~1) | int(binario_texto[index + 1]) if index + 1 < len(binario_texto) else g
                b = (b & ~1) | int(binario_texto[index + 2]) if index + 2 < len(binario_texto) else b
                pixeles[x, y] = (r, g, b)
                index += 3
            else:
                break

    imagen.save(output_path)
    return output_path

def extraer_texto_3des(imagen_path):
    imagen = Image.open(imagen_path)
    pixeles = imagen.load()
    ancho, alto = imagen.size
    binario_texto = []

    for y in range(alto):
        for x in range(ancho):
            r, g, b = pixeles[x, y]
            binario_texto.append(r & 1)
            binario_texto.append(g & 1)
            binario_texto.append(b & 1)

    byte_data = [int(''.join(map(str, binario_texto[i:i + 8])), 2) for i in range(0, len(binario_texto), 8)]
    try:
        texto_encriptado = bytes(byte_data)
        return desencriptar_texto_3des(texto_encriptado)
    except Exception as e:
        return str(e)

# === RUTAS DEL SERVIDOR ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    texto = request.form['texto']
    cifrado = request.form.get('cifrado', 'fernet')

    if file and texto:
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        if cifrado == 'fernet':
            output_path = ocultar_texto(file_path, texto)
        elif cifrado == '3des':
            output_path = ocultar_texto_3des(file_path, texto)
        else:
            return jsonify({"error": "Cifrado no soportado"}), 400

        return redirect(url_for('preview', image_path=output_path, image_or_path=file_path))

@app.route('/preview/<path:image_path>/<path:image_or_path>')
def preview(image_path, image_or_path):
    # Convertir las imágenes en binario para previsualización
    original_img = Image.open(image_or_path)
    encripted_img = Image.open(image_path)

    original_img_io = io.BytesIO()
    encripted_img_io = io.BytesIO()
    original_img.save(original_img_io, format="PNG")
    encripted_img.save(encripted_img_io, format="PNG")

    # Convertir las imágenes a base64
    original_img_base64 = base64.b64encode(original_img_io.getvalue()).decode('utf-8')
    encripted_img_base64 = base64.b64encode(encripted_img_io.getvalue()).decode('utf-8')

    # Obtener la matriz numérica de píxeles
    original_matriz = obtener_matriz_numerica(image_or_path)
    encripted_matriz = obtener_matriz_numerica(image_path)

    # Renderizar la plantilla pasando las imágenes y matrices numéricas
    return render_template(
        'preview.html',
        original_img=original_img_base64,
        encripted_img=encripted_img_base64,
        original_matriz=original_matriz,
        encripted_matriz=encripted_matriz
    )

@app.route('/download/<path:image_path>')
def download_image(image_path):
    return send_file(image_path, as_attachment=True)

@app.route('/extract', methods=['POST'])
def extract_text():
    file = request.files['file']
    cifrado = request.form.get('cifrado', 'fernet')

    if file:
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        if cifrado == 'fernet':
            texto = extraer_texto(file_path)
        elif cifrado == '3des':
            texto = extraer_texto_3des(file_path)
        else:
            return jsonify({"error": "Cifrado no soportado"}), 400

        return jsonify({"texto": texto})

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
