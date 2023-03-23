import logging
import json
import azure.functions as func


def main(req: func.HttpRequest, fieldAvailabilityIn: func.SqlRowList, fieldAvailabilityOut: func.Out[func.SqlRow], fieldReservations: func.Out[func.SqlRow]) -> func.HttpResponse:
    logging.info('Cancelling registration')

    try:
        codes = req.params.get('codes')
    except ValueError:
        pass

    if codes:
        ReservedTimeSlots = {
            1: ['19-20','11-12','15-16', '16-17', '17-18'],
            2: ['19-20','11-12','15-16', '16-17', '17-18'],
            3: ['19-20','09-10', '10-11', '11-12'],
            4: ['19-20','09-10', '10-11', '11-12'],
        }
        codesList = codes.split("|")
        rowsToAdjust = func.SqlRowList(map(lambda r: func.SqlRow.from_dict({"followcode": r, "cancelled":1}), codesList))
        fieldReservations.set(rowsToAdjust)
        currentReservationsToBeCancelled = list(map(lambda r: json.loads(r.to_json()), fieldAvailabilityIn))
        currentReservationsToBeCancelled = [x for x in currentReservationsToBeCancelled if x['followcode'] in codesList]
        cancelledRowsSql = func.SqlRowList(map(lambda r: func.SqlRow.from_dict({"followcode": r['followcode'],"field_number": r["field_number"], "timeslot":r["timeslot"] ,"busy":0}) if not r['timeslot'] in ReservedTimeSlots[r['field_number']] else func.SqlRow.from_dict({"followcode": None,"field_number": r["field_number"], "timeslot":r["timeslot"] ,"busy":1}), currentReservationsToBeCancelled))
        fieldAvailabilityOut.set(cancelledRowsSql)
        return func.HttpResponse(
            json.dumps(codesList),
            status_code=200
        )
    else:
        return func.HttpResponse(
            "Body is perhaps not in JSON or unreadable. Could not read body",
            status_code=400
        )
