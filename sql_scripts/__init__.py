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






