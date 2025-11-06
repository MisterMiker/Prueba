import paho.mqtt.client as paho
import time
import json
import streamlit as st
import cv2
import numpy as np
from PIL import Image
from keras.models import load_model

# Callback para cuando se publique un mensaje
def on_publish(client, userdata, result):
    print("El dato ha sido publicado\n")
    pass

# Callback para cuando se reciba un mensaje
def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write("Mensaje recibido:", message_received)

# Configuración del broker MQTT (debe coincidir con el del ESP32)
broker = "broker.hivemq.com"
port = 1883
client1 = paho.Client("CerraduraAPP")
client1.on_message = on_message
client1.on_publish = on_publish
client1.connect(broker, port)

# Cargar el modelo de Keras
model = load_model('keras_model.h5')
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# Interfaz Streamlit
st.title("🔒 Cerradura Inteligente con Visión Artificial")

img_file_buffer = st.camera_input("Toma una foto para abrir o cerrar la cerradura")

if img_file_buffer is not None:
    # Cargar imagen
    img = Image.open(img_file_buffer)
    newsize = (224, 224)
    img = img.resize(newsize)

    # Convertir a numpy y normalizar
    img_array = np.array(img)
    normalized_image_array = (img_array.astype(np.float32) / 127.0) - 1
    data[0] = normalized_image_array

    # Predicción
    prediction = model.predict(data)
    print(prediction)

    # Publicar mensaje MQTT según resultado
    if prediction[0][0] > 0.3:
        st.header('🔓 Abriendo cerradura...')
        client1.publish("IMIA", '{"gesto": "Abre"}', qos=0, retain=False)
        time.sleep(0.2)

    if prediction[0][1] > 0.3:
        st.header('🔒 Cerrando cerradura...')
        client1.publish("IMIA", '{"gesto": "Cierra"}', qos=0, retain=False)
        time.sleep(0.2)
