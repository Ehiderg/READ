from flask import Flask, jsonify, send_file
import pyodbc
import base64
import io
from datetime import datetime


app = Flask(__name__)

# Conexión a la base de datos
conn_str = 'DRIVER={SQL Server};SERVER=diseno2.database.windows.net;DATABASE=Diseño;UID=ehiderg;PWD=Diseño2023'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()


def agregar_log(cedula, tipo_documento,operacion, detalles):
    # Agregar registro al log
    cursor.execute("INSERT INTO Log (CedulaPersona, TipoDocumento, Operacion, FechaOperacion, Detalles) VALUES (?, ?, ?, ?, ?)",
                   cedula, tipo_documento, operacion, datetime.now(), detalles)
    conn.commit()

@app.route('/consultar/<numero_documento>', methods=['GET'])
def consultar(numero_documento):
    # Consultar en la base de datos
    cursor.execute("SELECT * FROM Registro WHERE NumeroDocumento=?", numero_documento)
    row = cursor.fetchone()

    if row:
        foto_data = base64.b64decode(row.Foto)
        foto_hex = foto_data.hex()
        # diccionario con los datos de la persona
        persona = {
            'TipoDocumento': row.TipoDocumento,
            'NumeroDocumento': row.NumeroDocumento,
            'PrimerNombre': row.PrimerNombre,
            'SegundoNombre': row.SegundoNombre,
            'Apellidos': row.Apellidos,
            'FechaNacimiento': row.FechaNacimiento,
            'Genero': row.Genero,
            'CorreoElectronico': row.CorreoElectronico,
            'Celular': row.Celular,
            'Foto': foto_hex  
        }
         
        
        agregar_log(row.NumeroDocumento, row.TipoDocumento, 'Consulta', f"Se consultó a la persona {row.PrimerNombre} {row.Apellidos}")

        return jsonify(persona), 200
    
    else:
        return jsonify({"error": "Persona no encontrada"}), 404
    
def obtener_foto(numero_documento):
    # Consultar en la base de datos para obtener la foto
    cursor.execute("SELECT Foto FROM Registro WHERE NumeroDocumento=?", numero_documento)
    row = cursor.fetchone()

    if row and row.Foto:
        # Decodificar la cadena base64 y devolver la imagen
        foto_data = base64.b64decode(row.Foto)
        return send_file(io.BytesIO(foto_data), mimetype='image/jpeg')

    else:
        return jsonify({"error": "Foto no encontrada"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
 
