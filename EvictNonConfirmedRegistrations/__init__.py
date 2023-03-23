from datetime import date, datetime, timedelta
import logging
import json
import azure.functions as func


def main(mytimer: func.TimerRequest, unconfirmedReservations: func.SqlRowList, fieldAvailability: func.Out[func.SqlRow], reservationExpired: func.Out[func.SqlRow]) -> None:
    utc_timestamp = datetime.utcnow()

    ReservedTimeSlots = {
        1: ['19-20','11-12','15-16', '16-17', '17-18'],
        2: ['19-20','11-12','15-16', '16-17', '17-18'],
        3: ['19-20','09-10', '10-11', '11-12'],
        4: ['19-20','09-10', '10-11', '11-12'],
    }


    unconfirmedRows = list(map(lambda r: json.loads(r.to_json()), unconfirmedReservations))
    five_days_ago = date.today() - timedelta(days=5)
    expiredRows = [x for x in unconfirmedRows if datetime.strptime(x['created_date'][0:x['created_date'].index('T')], "%Y-%m-%d").date() <= five_days_ago]
    expiredRowsReservationSql = func.SqlRowList(map(lambda r: func.SqlRow.from_dict({"followcode": r['followcode'], "expired":1}), expiredRows))
    expiredRowsFieldSql = func.SqlRowList(map(lambda r: func.SqlRow.from_dict({"followcode": r['followcode'],"field_number": r["field"], "timeslot":r["timeslot"] ,"busy":0}) if not r['timeslot'] in ReservedTimeSlots[r['field']] else func.SqlRow.from_dict({"followcode": None,"field_number": r["field"], "timeslot":r["timeslot"] ,"busy":1}), expiredRows))
    fieldAvailability.set(expiredRowsFieldSql)
    reservationExpired.set(expiredRowsReservationSql)

    if mytimer.past_due:
        logging.info('The timer is past due!')

    for x in expiredRowsReservationSql:
        logging.info("Expiring reservation with code " + x['followcode'])

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
