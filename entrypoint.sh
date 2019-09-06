#!/bin/sh
flask db upgrade
gunicorn -b 0.0.0.0:8000 main:app