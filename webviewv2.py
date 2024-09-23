import sys
import os
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
import platform

class PingThread(QThread):
    ping_result = pyqtSignal(bool, int)  # Señal para emitir el resultado del ping

    def __init__(self, urls, current_url):
        super().__init__()
        self.urls = urls
        self.current_url = current_url
        self.is_running = True

    def run(self):
        while self.is_running:
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

    def stop(self):
        """Detiene el hilo de manera segura."""
        self.is_running = False
        self.wait()  # Esperar a que el hilo termine


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
        self.ping_thread = None  # Para gestionar el hilo de ping
        self.load_url(self.urls[self.current_url])
        self.showFullScreen()
        self.clear_cookies_and_css()

    def load_url(self, url):
        self.browser.setUrl(QUrl(url))

    def check_connection(self):
        # Iniciar el hilo de ping solo si no hay un hilo ya ejecutándose
        if self.ping_thread is None or not self.ping_thread.isRunning():
            self.ping_thread = PingThread(self.urls, self.current_url)
            self.ping_thread.ping_result.connect(self.handle_ping_result)
            self.ping_thread.start()

    def handle_ping_result(self, is_connected, url_index):
        if is_connected:
            if url_index != self.current_url:
                self.current_url = url_index
                self.load_url(self.urls[self.current_url])
        else:
            self.show_no_connection_message()

    def show_no_connection_message(self):
        label = QLabel('Sin conexión a Internet, buscando conexión...', self)
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)

    def closeEvent(self, event):
        """Cerrar de manera segura el hilo al cerrar la ventana."""
        if self.ping_thread and self.ping_thread.isRunning():
            self.ping_thread.stop()  # Detener el hilo de manera segura
        event.accept()

    def clear_cookies_and_css(self):
        """Limpiar solo las cookies y el caché de CSS, manteniendo las contraseñas y datos de login."""
        profile = QWebEngineProfile.defaultProfile()
        
        # Eliminar solo cookies
        profile.cookieStore().deleteAllCookies()
        
        # Eliminar caché de archivos CSS específicamente
        def remove_css_cache():
            # Obtener directorio de la caché
            cache_path = profile.cachePath()
            
            # Recorrer el directorio y eliminar los archivos CSS
            for root, dirs, files in os.walk(cache_path):
                for file in files:
                    if file.endswith(".css"):
                        try:
                            os.remove(os.path.join(root, file))
                            print(f"Archivo CSS eliminado: {file}")
                        except Exception as e:
                            print(f"Error al eliminar archivo CSS: {e}")

        profile.clearHttpCache(remove_css_cache)

        print("Cookies y archivos CSS limpiados, datos de login preservados.")


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
