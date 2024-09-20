import sys
import os
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
import platform

class LoadUrlThread(QThread):
    def __init__(self, browser, url):
        super().__init__()
        self.browser = browser
        self.url = url

    def run(self):
        self.browser.setUrl(QUrl(self.url))

class FullScreenBrowser(QMainWindow):
    def __init__(self, urls):
        super().__init__()
        self.urls = urls
        self.current_url = 0
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_connection)
        self.timer.start(5000)  # Revisar conexión cada 5 segundos
        self.showFullScreen()
        self.load_url(self.urls[self.current_url])

    def load_url(self, url):
        self.thread = LoadUrlThread(self.browser, url)
        self.thread.start()  # Carga la URL en un hilo separado

    def check_connection(self):
        if self.ping(self.urls[self.current_url]):
            return  # Si la URL actual tiene conexión, no hacer nada
        else:
            for i, url in enumerate(self.urls):
                if self.ping(url):
                    self.current_url = i
                    self.load_url(url)
                    return
            
            # Si ninguna URL tiene conexión, mostrar mensaje
            self.show_no_connection_message()

    def show_no_connection_message(self):
        label = QLabel('Sin conexión a Internet, buscando conexión...', self)
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)

    def ping(self, url):
        # Extraer el host de la URL para hacer ping
        host = QUrl(url).host()
        
        # Diferenciar el comando ping según el sistema operativo
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        response = os.system(f"ping {param} 1 {host}")
        
        return response == 0

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    urls = [
        'http://172.25.30.240/live-weight/live.html?token=dfdfdsjhfwuegcjfwhmrdj',
        'https://dicaproduct.boisolo.dev/live-weight/live.html?token=dfdfdsjhfwuegcjfwhmrdj',
        'http://192.168.1.103/live.html?token=dfdfdsjhfwuegcjfwhmrdj'
    ]
    
    window = FullScreenBrowser(urls)
    sys.exit(app.exec_())
