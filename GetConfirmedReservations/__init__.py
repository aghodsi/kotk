import logging
import json
import azure.functions as func


def main(req: func.HttpRequest, confirmedReservations: func.SqlRowList) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    rows = list(map(lambda r: json.loads(r.to_json()), confirmedReservations))

    confirmed = req.params.get('confirmed')
    if not confirmed:
        confirmed = False
    elif confirmed == '1':
        confirmed = True
    
    rows = [x for x in rows if x['confirmed'] == confirmed]

    return func.HttpResponse(
        json.dumps(rows),
        status_code=200,
        mimetype="application/json"
    ) 