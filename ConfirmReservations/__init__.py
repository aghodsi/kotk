import logging
import json
import azure.functions as func


def main(req: func.HttpRequest, fieldReservations: func.Out[func.SqlRow]) -> func.HttpResponse:
    try:
        codes = req.params.get('codes')
    except ValueError:
        pass

    if codes:
        codesList = codes.split("|")
        rowsToAdjust = func.SqlRowList(map(lambda r: func.SqlRow.from_dict({"followcode": r, "confirmed":1}), codesList))
        fieldReservations.set(rowsToAdjust)
        return func.HttpResponse(
            json.dumps(codesList),
            status_code=200
        )
    else:
        return func.HttpResponse(
            "Body is perhaps not in JSON or unreadable. Could not read body",
            status_code=400
        )
