import logging
from datetime import datetime
import json
import azure.functions as func


def main(req: func.HttpRequest, reservationCode: func.SqlRowList, reservations: func.Out[func.SqlRow], fieldReservations: func.Out[func.SqlRow], followCodes: func.Out[func.SqlRow]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request. Saving Registration')

    try:
        req_body = req.get_json()
        req_body['followcode'] = reservationCode.data[0].get('code')
        req_body['confirmed'] = 0
        req_body['expired'] = 0
        req_body['cancelled'] = 0
        # reservationRow = func.SqlRowList(map(lambda r: func.SqlRow.from_dict(r), req_body))
        reservationRow = func.SqlRow.from_dict(req_body)

    except ValueError:
        pass

    if req_body:
        registration_reqs=("name", "email", "number_of_people", "field", "timeslot", "confirmed", "followcode", "activity_type")
        if not all(field in req_body for field in registration_reqs):
                return func.HttpResponse(
            "Body doesn't contain one of the necessary values.",
            status_code=400
            )
        fieldReservationRow = func.SqlRow.from_dict({"field_number": req_body["field"], "timeslot": req_body["timeslot"], "followcode": req_body['followcode'], "busy":1})
        followCodeRow = func.SqlRow.from_dict({"code": req_body["followcode"], "used":1})
        reservations.set(reservationRow)
        fieldReservations.set(fieldReservationRow)
        followCodes.set(followCodeRow)
        return func.HttpResponse(
            json.dumps(req_body),
            status_code=201,
            mimetype="application/json"
        )
    else:
        return func.HttpResponse(
            "Body is perhaps not in JSON or unreadable. Could not read body",
            status_code=400
        )
