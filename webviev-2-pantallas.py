import sys
import os
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSplitter, QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
import platform

class PingThread(QThread):
    ping_result = pyqtSignal(bool, int)  # Señal para emitir el resultado del ping

    def __init__(self, urls, current_url):
        super().__init__()
        self.urls = urls
        self.current_url = current_url

    def run(self):
        if self.ping(self.urls[self.current_url]):
            self.ping_result.emit(True, self.current_url)
        else:
            for i, url in enumerate(self.urls):
                if i != self.current_url and self.ping(url):
                    self.ping_result.emit(True, i)
                    return
            self.ping_result.emit(False, -1)

    def ping(self, url):
        # Extraer el host de la URL para hacer ping
        host = QUrl(url).host()
        
        # Diferenciar el comando ping según el sistema operativo
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        response = os.system(f"ping {param} 1 {host}")
        
        return response == 0

class FullScreenBrowser(QMainWindow):
    def __init__(self, urls):
        super().__init__()
        self.urls = urls
        self.current_url = 0
        
        # Crear el QSplitter para dividir la pantalla
        splitter = QSplitter(Qt.Horizontal)
        
        # Web principal
        self.browser_left = QWebEngineView()
        splitter.addWidget(self.browser_left)
        self.load_url(self.urls[self.current_url], self.browser_left)
        
        # Google en el lado derecho
        self.browser_right = QWebEngineView()
        splitter.addWidget(self.browser_right)
        self.load_url('https://www.google.es', self.browser_right)
        
        # Configurar el tamaño: 70% para la izquierda y 30% para la derecha
        splitter.setSizes([70, 30])
        
        self.setCentralWidget(splitter)
        
        # Configurar el temporizador para revisar la conexión
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_connection)
        self.timer.start(5000)  # Revisar conexión cada 5 segundos
        
        self.showFullScreen()

    def load_url(self, url, browser):
        browser.setUrl(QUrl(url))

    def check_connection(self):
        # Iniciar el hilo de ping
        self.ping_thread = PingThread(self.urls, self.current_url)
        self.ping_thread.ping_result.connect(self.handle_ping_result)
        self.ping_thread.start()

    def handle_ping_result(self, is_connected, url_index):
        if is_connected:
            if url_index != self.current_url:
                self.current_url = url_index
                self.load_url(self.urls[self.current_url], self.browser_left)
        else:
            self.show_no_connection_message()

    def show_no_connection_message(self):
        label = QLabel('Sin conexión a Internet, buscando conexión...', self)
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    urls = [
        'http://192.168.1.103/live.html?token=dfdfdsjhfwuegcjfwhmrdj',
        'http://172.25.30.240/live-weight/live.html?token=dfdfdsjhfwuegcjfwhmrdj',
        'https://dicaproduct.boisolo.dev/live-weight/live.html?token=dfdfdsjhfwuegcjfwhmrdj',
    ]

    window = FullScreenBrowser(urls)
    window.show()
    sys.exit(app.exec_())
