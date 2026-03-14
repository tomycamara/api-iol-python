import requests
import time
from settings import userName, passWord


class iolConection:

    def __init__(self, username, password):
        self.baseurl = "https://api.invertironline.com/api/v2/"
        self.auturl = "https://api.invertironline.com/token"

        self.usuario = username
        self.contra = password

        self.bearer = None
        self.refresh = None
        self.vence = None

    # login
    def login(self):

        userdata = {
            "username": self.usuario,
            "password": self.contra,
            "grant_type": "password"
        }

        header = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(self.auturl, data=userdata, headers=header)

        if response.status_code != 200 or response.status_code != 201:
            print(f"Error en login: {response.status_code},  {response.text}")

        data = response.json()

        self.bearer = data["access_token"]
        print("Token: ", self.bearer)
        self.refresh = data["refresh_token"]
        self.vence = time.time() + data["expires_in"] - 10

        print("Login exitoso")

    def refrescar(self):

        datos = {
            "refresh_token": self.refresh,
            "grant_type": "refresh_token"
        }

        header = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.post(self.auturl, data=datos, headers=header)

        if not response.ok:
            print("Error refrescando token")

        data = response.json()

        self.bearer = data["access_token"]
        self.refresh = data["refresh_token"]
        self.vence = time.time() + data["expires_in"] - 10

        print("Token refrescado")

    # VERIFICAR TOKEN
    def verificartoken(self):

        if self.bearer is None:
            self.login()

        elif time.time() >= self.vence:
            self.refrescar()

    # REQUEST BASE
    def request(self, metodo, endpoint, datos=None):

        self.verificartoken()

        url = f"{self.baseurl}{endpoint}?api_key={self.bearer}"

        header = {
            "Authorization": f"Bearer {self.bearer}",
            "Accept": "application/json"
        }

        response = requests.request(metodo, url, headers=header, data=datos)

        if not response.ok:
            raise Exception(f"Error {response.status_code}: {response.text}")

        return response.json()

    # get y post generales
    def get(self, endpoint):
        return self.request("GET", endpoint)

    def post(self, endpoint, datos):
        return self.request("POST", endpoint, datos)

    # endpoint especifico
    def obtener_perfil(self):
        return self.get("datos-perfil")

    def consultar_orden(self, orden):
        return self.get(f"ordenes/{orden}")
    

    def cotizarmep(self, simbolo):
        aux = {
        "simbolo": simbolo,
        "idPlazoOperatoriaCompra": 1,
        "idPlazoOperatoriaVenta": 1
        }
        return self.post("Cotizaciones/MEP", aux)


class usuario:

    def __init__(self, username, password):
        self.networking = iolConection(username, password)

    def iniciar(self):
        self.networking.login()

    def muestraPerfil(self):

        perfil = self.networking.obtener_perfil()

        print("Nombre:", perfil["nombre"])
        print("Cuenta:", perfil["numeroCuenta"])

    def cotizacion(self, simbolo):
        print(F"La cotizacion de {simbolo} respecto al MEP es:",self.networking.cotizarmep(simbolo))

if __name__ == "__main__":
    simbolo = "GD35"
    app = usuario(userName, passWord)

    app.iniciar()

    app.muestraPerfil()

    app.cotizacion(simbolo)