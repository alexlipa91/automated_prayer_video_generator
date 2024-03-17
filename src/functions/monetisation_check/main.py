import functions_framework
import json

@functions_framework.http
def run(request):
    status = request.args["status"].lower()
    entry = dict(
        message="Automa workflow finished with status {}".format(status),
        status=status,
    )
    print(json.dumps(entry))
    return {}, 200
