import json

import requests
import functions_framework


class Controller:

    def __init__(self):
        url = "https://console.kamatera.com/service/authenticate"
        payload = """{"clientId":"054825733b501db5e1947de3a46212f4", "secret":"7462704418fa0a9789f31f4de3d3c2ee"}"""
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        self.token = json.loads(response.text)["authentication"]

    def power(self, power):
        url = "https://console.kamatera.com/service/server/4236bbe4-f933-1c1f-32fe-2e08ef60926c/power"
        payload = json.dumps({"power": power})
        headers = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.token)}
        response = requests.request("PUT", url, headers=headers, data=payload)
        return response


@functions_framework.http
def run(request):
    c = Controller()
    print(c.power(request.args.get('power')))
    return "ok"
