from typing import List

import psycopg2

from config import config

connection = psycopg2.connect(
    database=config.db_name,
    user=config.db_user,
    password=config.db_password,
    host=config.db_host,
    port=config.db_port)


def get_unique_4_letter_codes():
    pass


def get_course_list() -> List[str]:
    with connection.cursor() as curr:
        curr.execute('''
            SELECT c_code FROM "Course" 
        ''')
        return [x[0] for x in curr.fetchall()]
