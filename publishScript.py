# # from certs import caCertFile
# # from certs import certFile
# # from certs import certKey

# import ssl
# import paho.mqtt.client as mqtt

# # Configuración del servidor MQTT
# mqtt_broker_address = "157.230.187.251"
# mqtt_port = 1883  # Puerto seguro para SSL
# mqtt_topic = "testtopic/1"
# mqtt_username = "Daniel"
# mqtt_password = ""



# # Configuración de SSL/TLS
ca_cert_path = "./certs/cacert.pem" # Ruta al certificado de la CA del servidor
# client_cert_path = "./certs/cert.pem"  # Ruta al certificado del cliente
# client_key_path = "./certs/key.pem"  # Ruta a la clave privada del cliente

# def on_connect(client, userdata, flags, rc):
#     print(f"Conectado con código de resultado {rc}")
#     client.subscribe(mqtt_topic)

# def on_publish(client, userdata, mid):
#     print(f"Mensaje publicado con ID: {mid}")

# # Crear cliente MQTT
# client = mqtt.Client()

# # Configurar certificados SSL/TLS
# client.tls_set(
#     ca_certs=ca_cert_path, 
#     certfile=None, #client_cert_path,
#     keyfile=None, #client_key_path, 
#     cert_reqs=ssl.CERT_REQUIRED,
#     tls_version=ssl.PROTOCOL_TLSv1_2,
#     ciphers=None,
# )

# # Configurar eventos de conexión y publicación
# client.on_connect = on_connect
# client.on_publish = on_publish

# # Autenticación (si es necesario)
# # client.username_pw_set(username=mqtt_username, password=mqtt_password)

# # Conectar al servidor MQTT
# client.connect(mqtt_broker_address, mqtt_port, keepalive=60)

# # Publicar un mensaje
# mensaje = """{
#     temperatura : 25,
#     id: 26,
# }"""
# result, mid = client.publish(mqtt_topic, mensaje, qos=1)

# # Esperar a que se envíen los mensajes
# client.loop_forever()



# python 3.x

import json
import logging
import random
import time

from paho.mqtt import client as mqtt_client

BROKER = '157.230.187.251'
PORT = 8883
TOPIC = "testtopic/1"
# generate client ID with pub prefix randomly
CLIENT_ID = f'python-mqtt-tls-pub-{random.randint(0, 1000)}'
USERNAME = 'emqx'
PASSWORD = 'public'
FLAG_CONNECTED = 0

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

FLAG_EXIT = False


def on_connect(client, userdata, flags, rc):
    if rc == 0 and client.is_connected():
        print("Connected to MQTT Broker!")
    else:
        print(f'Failed to connect, return code {rc}')


def on_disconnect(client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
    global FLAG_EXIT
    FLAG_EXIT = True


def connect_mqtt():
    client = mqtt_client.Client(CLIENT_ID,)
    # 
    client.tls_set(ca_certs=ca_cert_path)
    client.tls_insecure_set(True)
    
    # client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.connect(BROKER, PORT, keepalive=120)
    client.on_disconnect = on_disconnect
    return client


def publish(client):
    msg_count = 0
    while not FLAG_EXIT:
        msg_dict = {
            'msg': msg_count
        }
        msg = json.dumps(msg_dict)
        if not client.is_connected():
            logging.error("publish: MQTT client is not connected!")
            time.sleep(1)
            continue
        result = client.publish(TOPIC, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f'Send `{msg}` to topic `{TOPIC}`')
        else:
            print(f'Failed to send message to topic {TOPIC}')
        msg_count += 1
        time.sleep(1)


def run():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.DEBUG)
    client = connect_mqtt()
    client.loop_start()
    time.sleep(1)
    if client.is_connected():
        publish(client)
    else:
        client.loop_stop()


if __name__ == '__main__':
    run()