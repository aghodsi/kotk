import logging
import json
import azure.functions as func


def main(req: func.HttpRequest, availabilities: func.SqlRowList, reservationsKids: func.SqlRowList, reservationsWorkout: func.SqlRowList) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request. In GetAvailableTimeSlots')

    limit_per_hour_kids = 12
    limit_per_hour_workout = 12

    timeslot = req.params.get('timeslot')
    activityType = req.params.get('activityType')
    if not timeslot:
        return func.HttpResponse("You need to provide a timeslot.", status_code=400)
    elif not activityType:
        return func.HttpResponse("You need to provide activity.", status_code=400)
    else:
        if activityType == 'kids':
            rows = list(map(lambda r: json.loads(r.to_json()), reservationsKids))
            rows_field_three = [x for x in rows if x['timeslot'] == timeslot and x['field'] == 3]
            rows_field_four = [x for x in rows if x['timeslot'] == timeslot and x['field'] == 4]
            availableFieldsList = []
            if len(rows_field_three) < limit_per_hour_kids:
                availableFieldsList.append({"field_number":3})
            if len(rows_field_four) < limit_per_hour_kids:
                availableFieldsList.append({"field_number":4})
            return func.HttpResponse(
                json.dumps(availableFieldsList),
                status_code=200,
                mimetype="application/json"
            ) 
        elif activityType == 'workout':
            rows = list(map(lambda r: json.loads(r.to_json()), reservationsWorkout))
            rows_field_one = [x for x in rows if x['timeslot'] == timeslot and x['field'] == 1]
            rows_field_two = [x for x in rows if x['timeslot'] == timeslot and x['field'] == 2]
            availableFieldsList = []
            if len(rows_field_one) < limit_per_hour_workout:
                availableFieldsList.append({"field_number":1})
            if len(rows_field_two) < limit_per_hour_workout:
                availableFieldsList.append({"field_number":2})
            return func.HttpResponse(
                json.dumps(availableFieldsList),
                status_code=200,
                mimetype="application/json"
            ) 
        else:
            # activity type is nor kids or nor workout, so must be marathon. No additional checks.
            rows = list(map(lambda r: json.loads(r.to_json()), availabilities))
            rows = [x for x in rows if x['timeslot'] == timeslot]

            return func.HttpResponse(
                json.dumps(rows),
                status_code=200,
                mimetype="application/json"
            ) 
