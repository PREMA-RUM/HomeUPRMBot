from typing import List

import psycopg2

from config import config

connection = psycopg2.connect(
    database=config.db_name,
    user=config.db_user,
    password=config.db_password,
    host=config.db_host,
    port=config.db_port)


def get_course_list() -> List[str]:
    with connection.cursor() as curr:
        curr.execute('''
            SELECT c_code, c_id FROM "Course" 
        ''')
        return [x for x in curr.fetchall()]


def get_or_create_semester_return_id(semester):
    with connection.cursor() as curr:
        curr.execute('''
                    SELECT s_id FROM "Semester" 
                    where t_id = %s and s_year = %s
                ''', (semester['term'], semester['year']))
        semester_id = curr.fetchone()
        if semester_id is not None:
            return semester_id[0]
        curr.execute('''
                            insert into "Semester" (t_id, s_year) 
                            VALUES ( %s, %s ) 
                            returning s_id;
                        ''', (semester['term'], semester['year']))
        return curr.fetchone()[0]


# semester_offer_data = (section, capacity, start_time, end_time, classroom, professor, days_id_list)
def semester_offer_data_exists_in_prod(semester_offer_data, semester_id, course_id):
    result = []
    query = '''
               SELECT so_id FROM "SemesterOffer" 
               WHERE so_section_name = \'%s\' and c_id = %d and so_classroom = \'%s\' and s_id = %d
           ''' % (semester_offer_data[0], course_id, semester_offer_data[4], semester_id)

    with connection.cursor() as curr:
        curr.execute(query)
        result = curr.fetchone()

    return -1 if result is None else result[0]


# semester_offer_data = (section, capacity, start_time, end_time, classroom, professor, days_id_list)
def create_semester_offer(semester_offer_data, semester_id, course_id):
    result = []
    query = '''
                   INSERT INTO "SemesterOffer" (so_capacity, so_section_name, c_id, s_id, so_classroom)
                   VALUES ( %d, \'%s\', %d, %d, \'%s\' )
                   RETURNING so_id
               ''' % (semester_offer_data[1], semester_offer_data[0], course_id, semester_id, semester_offer_data[4])

    with connection.cursor() as curr:
        curr.execute(query)
        result = curr.fetchone()
    return -1 if result is None else result[0]


# semester_offer_data = (section, capacity, start_time, end_time, classroom, professor, days_id_list)
def create_semester_offer_timeslots(semester_offer_data, semester_offer_id):
    for day_id in semester_offer_data[6]:
        query = '''
                           INSERT INTO "TimeSlot" (ts_start_time, ts_end_time, so_id, d_id)
                           VALUES ( \'%s\'::time, \'%s\'::time, %d, %d )
                       ''' % (semester_offer_data[2], semester_offer_data[3], semester_offer_id, day_id)

        with connection.cursor() as curr:
            curr.execute(query)
