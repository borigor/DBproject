__author__ = 'igor'

import MySQLdb as db


class DBConnector:

    def __init__(self):
        pass

    def connect(self):
        return db.connect(self.host,
                          self.user,
                          self.password,
                          self.dataBase,
                          init_command='set names UTF8')
    host = "localhost"
    user = "root"
    password = "straustrup288"
    dataBase = "DBproject"


def update_query(query, params):
    try:
        connector = DBConnector()
        connector = connector.connect()
        cursor = connector.cursor()
        cursor.execute(query, params)
        connector.commit()
        inserted_id = cursor.lastrowid

        cursor.close()
        connector.close()
    except db.Error:
        raise db.Error("Database error in update query.")
    return inserted_id


def select_query(query, params):
    try:
        connector = DBConnector()
        connector = connector.connect()
        cursor = connector.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        connector.close()
    except db.Error:
        raise db.Error("Database error in usual query")
    return result


def exist(entity, identifier, value):
    if not len(select_query("SELECT id FROM " + entity + " WHERE " + identifier + " =%s", (value, ))):
        raise Exception("No such element in " + entity + " with " + identifier + "=" + str(value))
    return


def clear():
    sql = ["SET foreign_key_checks = 0;",
        "truncate Followers;",
        "truncate Forums;",
        "truncate Posts;",
        "truncate Subscriptions;",
        "truncate Threads;",
        "truncate Users;",
        "SET foreign_key_checks = 1;"]
    try:
        connector = DBConnector()
        connector = connector.connect()
        with connector:
            cursor = connector.cursor()
            for query in sql:
                cursor.execute(query)
                connector.commit()
            cursor.close()
        connector.close()
    except db.Error:
        raise db.Error("Database error")
    return