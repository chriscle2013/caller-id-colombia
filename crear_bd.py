# crear_bd.py - Crear base de datos de reportes
import sqlite3
from datetime import datetime

def crear_base_datos():
    conn = sqlite3.connect('reportes_spam.db')
    cursor = conn.cursor()
    
    # Tabla de números reportados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS numeros_reportados (
            numero TEXT PRIMARY KEY,
            reportes INTEGER DEFAULT 1,
            ultimo_reporte TIMESTAMP,
            categoria TEXT DEFAULT 'spam',
            riesgo TEXT DEFAULT 'low'
        )
    ''')
    
    # Tabla de reportes individuales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reportes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT,
            categoria TEXT,
            comentario TEXT,
            ip TEXT,
            fecha TIMESTAMP,
            FOREIGN KEY (numero) REFERENCES numeros_reportados (numero)
        )
    ''')
    
    # Insertar algunos números conocidos como ejemplo
    numeros_spam = [
        ("57300111222", 5, "high", "Llamadas de cobranza"),
        ("57300222333", 3, "medium", "Telemarketing"),
        ("57300333444", 10, "high", "Estafa"),
    ]
    
    for num, reportes, riesgo, motivo in numeros_spam:
        cursor.execute('''
            INSERT OR REPLACE INTO numeros_reportados 
            (numero, reportes, ultimo_reporte, categoria, riesgo)
            VALUES (?, ?, ?, ?, ?)
        ''', (num, reportes, datetime.now().isoformat(), motivo, riesgo))
    
    conn.commit()
    conn.close()
    print("✅ Base de datos creada exitosamente")
    print("📊 Se agregaron números de ejemplo")

if __name__ == "__main__":
    crear_base_datos()
