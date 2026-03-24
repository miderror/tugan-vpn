import orjson
from django.http import HttpResponse

R204 = HttpResponse(status=204)
R400 = HttpResponse(status=400)
R401 = HttpResponse(status=401)
R404 = HttpResponse(status=404)
R405 = HttpResponse(status=405)
R500 = HttpResponse(status=500)


def fast_json(data, status=200):
    return HttpResponse(
        orjson.dumps(data), content_type="application/json", status=status
    )
