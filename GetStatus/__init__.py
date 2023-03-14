import logging
import json
import azure.functions as func


def main(req: func.HttpRequest, reservationStatus: func.SqlRowList) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    rows = list(map(lambda r: json.loads(r.to_json()), reservationStatus))

    code = req.params.get('code')
    if not code:
        return func.HttpResponse("You need to provide a code.", status_code=400)
    else:
        rows = [x for x in rows if x['followcode'] == code]

    return func.HttpResponse(
        json.dumps(rows),
        status_code=200,
        mimetype="application/json"
    ) 
