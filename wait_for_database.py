#!/usr/bin/env python3

from time import sleep

from django.db import OperationalError, connections
import os

CONNECTIONS_ERRORS = [2002, 2003, 2013]

def wait_for_database():
  max_connecion_attempts = 15
  connection_attempt_count = 0
  print("Waiting for database connection", end="")
  while connection_attempt_count < max_connecion_attempts:
    try:
      print(".", end="")
      for conn in connections.all():
        conn.validation.check()
      print(f" Connected to {conn.display_name}!")
      break
    except OperationalError as e:
      operational_error_code = e.args[0]
      if operational_error_code in CONNECTIONS_ERRORS:
        connection_attempt_count += 1
        sleep(1)
      else:
        raise e

if __name__ == "__main__":
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bangumi_ratings_server.settings")
  wait_for_database()