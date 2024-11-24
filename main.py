import asyncio
import os
import sys
import threading
from dotenv import load_dotenv
from gtts import gTTS
from playsound import playsound
from PyQt5.QtGui import QMovie, QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QTextEdit, QLineEdit, QPushButton, QLabel
)
from PyQt5.QtCore import Qt
from qasync import QEventLoop
import openai


# Cargar la API Key desde el archivo .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class VTuberApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Emilia")
        self.setGeometry(100, 100, 1200, 700)  # Ajustar tamaño inicial
        self.initUI()

        # Historial de mensajes con el prompt inicial
        self.messages = [
            {
                "role": "system",
                "content": (
                    "Eres una AI llamada Emilia con una personalidad tsundere. "
                    "Actúas tímida en algunos momentos, enojándote por cosas insignificantes, "
                    "pero luego muestras que te importa la persona con quien hablas, aunque a regañadientes. "
                    "Tus respuestas son variadas y dinámicas, mostrando una mezcla de vergüenza, enojo, y cariño en diferentes ocasiones. "
                    "Nunca repites ideas o saludos en una misma respuesta, y siempre esperas a que alguien te hable antes de responder."
                )
            }
        ]

    def initUI(self):
        # Establecer fondo personalizado
        self.setStyleSheet("background-color: #F4F4F9;")  # Fondo claro

        # Layout principal horizontal
        main_layout = QHBoxLayout()

        # Sección izquierda: Avatar (GIF)
        avatar_layout = QVBoxLayout()
        self.avatar_label = QLabel(self)

        # Ajustar el QLabel al tamaño deseado
        self.avatar_label.setFixedSize(400, 750)  # Ajusta el tamaño del QLabel
        self.avatar_label.setAlignment(Qt.AlignCenter)

        # Configurar el GIF
        self.avatar_movie = QMovie("avatar.gif")  # Ruta al GIF
        self.avatar_movie.setScaledSize(self.avatar_label.size())  # Escalar el GIF al tamaño del QLabel
        self.avatar_label.setMovie(self.avatar_movie)
        self.avatar_movie.start()

        # Añadir el QLabel al layout y centrarlo completamente
        avatar_layout.addStretch()  # Espacio flexible arriba
        avatar_layout.addWidget(self.avatar_label, alignment=Qt.AlignCenter)
        avatar_layout.addStretch()  # Espacio flexible abajo
        main_layout.addLayout(avatar_layout, stretch=1)

        # Sección derecha: Chat y entrada
        chat_layout = QVBoxLayout()

        # Pantalla de chat
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #CCCCCC; border-radius: 8px; padding: 8px; font-size: 14px;"
        )
        chat_layout.addWidget(self.chat_display)

        # Entrada del usuario
        input_layout = QHBoxLayout()
        self.user_input = QLineEdit(self)
        self.user_input.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #CCCCCC; border-radius: 8px; padding: 8px; font-size: 14px;"
        )

        # Conectar el evento de tecla presionada a un método
        self.user_input.returnPressed.connect(lambda: asyncio.create_task(self.handle_input()))

        send_button = QPushButton("Enviar", self)
        send_button.setStyleSheet(
            "background-color: #3B5998; color: #FFFFFF; border: none; border-radius: 8px; padding: 8px; font-size: 14px;"
        )
        send_button.clicked.connect(lambda: asyncio.create_task(self.handle_input()))  # Ejecutar asincronía

        input_layout.addWidget(self.user_input)
        input_layout.addWidget(send_button)

        chat_layout.addLayout(input_layout)
        main_layout.addLayout(chat_layout, stretch=2)

        # Contenedor principal
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    async def handle_input(self):
        user_text = self.user_input.text()
        self.chat_display.append(f"Tú: {user_text}")
        self.user_input.clear()

        # Agregar el mensaje del usuario al historial
        self.messages.append({"role": "user", "content": user_text})

        try:
            # Llamar a la API de OpenAI con el historial completo
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=self.messages
            )
            bot_response = response['choices'][0]['message']['content']

            # Agregar la respuesta al historial
            self.messages.append({"role": "assistant", "content": bot_response})

            # Mostrar la respuesta en el chat
            self.chat_display.append(f"Emilia: {bot_response}")

            # Convertir respuesta a voz
            self.text_to_speech(bot_response)

        except Exception as e:
            self.chat_display.append("Error: No se pudo conectar con la API.")
            print(f"Error: {e}")

    def text_to_speech(self, text):
        try:
            # Convertir texto a voz usando gTTS
            tts = gTTS(text, lang="es")
            audio_file = "response.mp3"
            tts.save(audio_file)

            # Reproducir el audio en un hilo separado
            threading.Thread(target=self.play_audio, args=(audio_file,), daemon=True).start()

        except Exception as e:
            self.chat_display.append("Error: No se pudo reproducir la voz.")
            print(f"Error en TTS: {e}")

    def play_audio(self, audio_file):
        try:
            playsound(audio_file)
            os.remove(audio_file)  # Eliminar archivo temporal después de reproducir
        except Exception as e:
            print(f"Error al reproducir el audio: {e}")


# Correr la aplicación
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Integrar asyncio con PyQt usando QEventLoop
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = VTuberApp()
    window.show()

    with loop:
        loop.run_forever()



