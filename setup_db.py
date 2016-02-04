#!/usr/bin/env python3

import argparse
import os.path
import sqlite3
import sys

def create_db(location):
    return sqlite3.connect(location)

def setup_schema(conn):
    c = conn.cursor()
    with open('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

    conn.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("db", help="Name of the database")
    parser.add_argument("-f", "--force", help="Force creation of DB",
                        action="store_true")
    parser.add_argument("-l", "--location", help="Location of the database")

    args = parser.parse_args()

    if args.location is None:
        db_location = "./{0}.db".format(args.db)
    else:
        db_location = args.location

    print(args.location)
    print(db_location)

    if os.path.exists(db_location) and not args.force:
        overwrite_db = input("DB already exists. Recreate it? [y/N] ")
        if overwrite_db.lower() == "y":
            os.remove(db_location)
        else:
            sys.exit(0)

    conn = create_db(db_location)
    setup_schema(conn)

    conn.close()
