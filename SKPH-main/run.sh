#!/bin/sh
# pybabel extract -F babel.cfg -o messages.pot . # Extracts texts from templates to translations
# pybabel update -i messages.pot -d translations # Updates polish translations dictionary
# pybabel compile -d translations # Compile translations
flask run
