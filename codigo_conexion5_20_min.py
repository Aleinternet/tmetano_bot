import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

# Telegram
BOT_TOKEN = "7447515195:AAHoLThGSNBTsAREsKIFKwyZLyoBJw_X_No"
CHAT_ID = "7925190252"

# SINCA
url = "https://sinca.mma.gob.cl/cgi-bin/registrostable2k19.cgi?domain=CONAMA&stn=D13"

def obtener_dato_mp10():
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    div_marco = soup.find('div', class_='marco')
    if not div_marco:
        return None

    tabla = div_marco.find('table')
    if not tabla:
        return None

    filas = tabla.tbody.find_all('tr')
    datos = []

    for fila in filas:
        celdas = fila.find_all('td')
        if len(celdas) >= 4:
            fecha = celdas[0].get_text(strip=True)
            hora = celdas[1].get_text(strip=True)
            mp10 = celdas[3].get_text(strip=True)
            if mp10 and mp10 not in ['-', '—', '']:
                try:
                    mp10_val = float(mp10.replace(',', '.'))
                    datos.append({'fecha': fecha, 'hora': hora, 'mp10': mp10_val})
                except ValueError:
                    pass

    if datos:
        return datos[-1]
    else:
        return None

def enviar_telegram_mensaje(texto):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": texto}
    requests.post(url, data=payload)

# 🕐 Bucle que se ejecuta cada 20 minutos
while True:
    print(f"\nBuscando dato MP10... ({datetime.now().strftime('%H:%M:%S')})")
    dato = obtener_dato_mp10()

    if dato:
        valor = int(round(dato['mp10']))  # sin decimales
        mensaje_telegram = f"HOY:{valor} µg/m³"

        # Impresión más detallada
        print(f"Último dato Las Condes MP10: {dato['mp10']} µg/m³")
        print(f"Fecha: {dato['fecha']}")
        print(f"Hora: {dato['hora']}")
        print(f"Mensaje: {mensaje_telegram}")

        # Enviar solo el mensaje simplificado
        enviar_telegram_mensaje(mensaje_telegram)
    else:
        print("No se pudo obtener dato válido.")

    # Esperar 20 minutos (1200 segundos)
    time.sleep(20 * 60)
