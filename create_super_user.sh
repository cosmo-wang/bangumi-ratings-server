#!/usr/bin/env sh
set -eu

HERE="$( cd "$( dirname "${0}" )" && pwd )"
cd "${HERE}"

SUPERUSER_ID="admin"
SUPERUSER_PASSWORD="password"

cmd=""
cmd="${cmd}from django.contrib.auth.models import User;"
cmd="${cmd}User.objects.filter(username='${SUPERUSER_ID}').delete();"
cmd="${cmd}User.objects.create_superuser('${SUPERUSER_ID}', password='${SUPERUSER_PASSWORD}');"
pythonCreateUserCommand="${cmd}"

echo "${pythonCreateUserCommand}" | ./manage.py shell
echo "Superuser '${SUPERUSER_ID}' created!"
