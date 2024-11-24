# Importar módulos estándar de Python
import asyncio  # Para manejar tareas asincrónicas
import openai  # Para interactuar con la API de OpenAI
import os  # Para manejar operaciones del sistema operativo
import sys  # Para manejar operaciones del sistema y argumentos del script
import threading  # Para manejar hilos de ejecución

# Importar módulos de terceros
from dotenv import load_dotenv  # Para cargar variables de entorno desde un archivo .env
from google.cloud import texttospeech  # Cliente para Google Cloud Text-to-Speech
from playsound import playsound  # Para reproducir archivos de audio

# Importar módulos específicos de PyQt5
from PyQt5.QtCore import Qt  # Para configuraciones generales de PyQt (alineación, etc.)
from PyQt5.QtGui import QMovie  # Para manejar animaciones en formato GIF
from PyQt5.QtWidgets import (  # Para crear y gestionar la interfaz gráfica
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QTextEdit, QLineEdit, QPushButton, QLabel
)

# Integración de asyncio con PyQt
from qasync import QEventLoop  # Permite usar asyncio en aplicaciones PyQt

# Función para obtener rutas de archivos empaquetados con PyInstaller
def resource_path(relative_path):
    """Obtén la ruta absoluta del recurso, compatible con PyInstaller."""
    if hasattr(sys, '_MEIPASS'):  # Directorio temporal creado por PyInstaller
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Configurar credenciales de Google Cloud TTS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = resource_path("tts-credentials.json")

# Cargar la API Key desde el archivo .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class EmiliaChatApp(QMainWindow):
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

class EmiliaChatApp(QMainWindow):
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
        # Crear menú principal
        self.create_menu()

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
        gif_path = resource_path("avatar.gif")  # Usar ruta empaquetada
        self.avatar_movie = QMovie(gif_path)  # Ruta al GIF
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

    def create_menu(self):
        """Crea el menú principal de la aplicación."""
        menu_bar = self.menuBar()

        # Crear menú "Opciones"
        options_menu = menu_bar.addMenu("Opciones")

        # Opción "Salir"
        exit_action = options_menu.addAction("Salir")
        exit_action.triggered.connect(self.close)  # Conectar al método close()

        # Estilo para evitar el cambio de color en "mouseover"
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #F4F4F9;  /* Color del fondo del menú */
            }
            QMenuBar::item {
                background-color: #F4F4F9;  /* Fondo de los items */
                color: #000000;  /* Color del texto */
            }
            QMenuBar::item:selected {  /* Al hacer hover */
                background-color: #E0E0E0;  /* Fondo del item seleccionado */
                color: #000000;  /* Mantener el color del texto */
            }
            QMenu {
                background-color: #FFFFFF;  /* Fondo del menú desplegable */
                border: 1px solid #CCCCCC;  /* Borde del menú */
            }
            QMenu::item {
                background-color: #FFFFFF;  /* Fondo de los items */
                color: #000000;  /* Color del texto */
            }
            QMenu::item:selected {  /* Al hacer hover */
                background-color: #E0E0E0;  /* Fondo del item seleccionado */
                color: #000000;  /* Mantener el color del texto */
            }
        """)

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
            # Configurar cliente de Google Cloud TTS
            client = texttospeech.TextToSpeechClient()

            # Configurar la solicitud de síntesis
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="es-MX",  # Cambiar a al idioma/acento preferido
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE  # Cambiar el género de la voz
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            # Generar el audio
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            # Guardar el archivo de audio
            audio_file = "response.mp3"
            with open(audio_file, "wb") as out:
                out.write(response.audio_content)

            # Reproducir el audio
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

    window = EmiliaChatApp()
    window.show()

    with loop:
        loop.run_forever()