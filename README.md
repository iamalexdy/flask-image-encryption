# Proyecto de Esteganografía con Flask

Este proyecto permite ocultar y extraer mensajes dentro de imágenes utilizando dos métodos de cifrado: **Fernet (AES)** y **3DES**. Además, incluye previsualización de la imagen original, la imagen encriptada y sus representaciones numéricas de píxeles.

## 🚀 Requisitos

- Python 3.8+
- pip

## 📦 Instalación

1. Clona el repositorio:
   ```powershell
   git clone https://github.com/usuario/Esteganografia.git
   cd Esteganografia
   ```

2. Crea un entorno virtual:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```powershell
   pip install flask pillow cryptography pycryptodome numpy
   ```

## ▶️ Ejecución

Inicia el servidor con:
```powershell
python app.py
```

Abre tu navegador y entra en:
```
http://127.0.0.1:5000 o el que indique la terminal
```

## 📂 Estructura del proyecto

```
Esteganografia/
│── app.py
│── requirements.txt
│── templates/
│   ├── index.html
│   └── preview.html
│── uploads/
│── static/
│   └── styles.css
```

## 🖼️ Funcionalidades

- Subir imagen y ocultar un mensaje en ella.
- Seleccionar método de cifrado (**Fernet o 3DES**).
- Previsualizar imagen original y encriptada.
- Ver representación numérica de cada píxel (0-255).
- Descargar imagen encriptada.
- Extraer mensajes ocultos desde imágenes.

