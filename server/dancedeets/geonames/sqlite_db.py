import logging


def insert_record(cursor, table_name, data):
    key_values = data.items()

    insert_sql = 'INSERT OR IGNORE INTO %s (%s) VALUES (%s)' % (
        table_name,
        ', '.join(kv[0] for kv in key_values),
        ', '.join('?' for kv in key_values),
    )
    try:
        result = cursor.execute(insert_sql, [kv[1] for kv in key_values])
    except Exception:
        logging.exception('Found problems with data: %s', data)
        result = None
    cursor.connection.commit()
    return result
