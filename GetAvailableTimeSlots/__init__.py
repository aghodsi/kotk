import logging
import json
import azure.functions as func


def calc_sum(rows):
    sum = 0
    for r in rows:
        sum += r['number_of_people']
    return sum

def build_list(rows, field_1, field_2, timeslot,  limit, number_of_people):
    rows = list(map(lambda r: json.loads(r.to_json()), rows))
    rows_field_one = [x for x in rows if x['timeslot'] == timeslot and x['field'] == field_1]
    rows_field_two = [x for x in rows if x['timeslot'] == timeslot and x['field'] == field_2]
    sumTotalPeopleFieldOne = calc_sum(rows_field_one)
    sumTotalPeopleFieldTwo = calc_sum(rows_field_two)

    availableFieldsList = []
    if (limit - sumTotalPeopleFieldOne - number_of_people) >=0:
        availableFieldsList.append({"field_number":field_1})
    if (limit - sumTotalPeopleFieldTwo - number_of_people) >=0:
        availableFieldsList.append({"field_number":field_2})
    return availableFieldsList

def main(req: func.HttpRequest, availabilities: func.SqlRowList, reservationsKids: func.SqlRowList, reservationsWorkout: func.SqlRowList) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request. In GetAvailableTimeSlots')

    limit_per_hour_kids = 12
    limit_per_hour_workout = 8

    timeslot = req.params.get('timeslot')
    activityType = req.params.get('activityType')
    if not timeslot:
        return func.HttpResponse("You need to provide a timeslot.", status_code=400)
    elif not activityType:
        return func.HttpResponse("You need to provide activity.", status_code=400)
    else:
        if (activityType == 'kids' or activityType == 'workout') and not req.params.get('numberOfPeople'):
            return func.HttpResponse("You need to provide the number of people so we can see if the fields are already overpopulated or not.", status_code=400)
        if activityType == 'kids':
            number_of_people_requested = req.params.get('numberOfPeople')
            availableFieldsList = build_list(reservationsKids, '3', '4', timeslot, limit_per_hour_kids, int(number_of_people_requested))
            return func.HttpResponse(
                json.dumps(availableFieldsList),
                status_code=200,
                mimetype="application/json"
            ) 
        elif activityType == 'workout':
            number_of_people_requested = req.params.get('numberOfPeople')
            availableFieldsList = build_list(reservationsWorkout, '1', '2', timeslot, limit_per_hour_workout, int(number_of_people_requested))
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

