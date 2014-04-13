#!/bin/bash
set -v
rm -rf .chucky
#python chucky.py --interactive msn_parse_oim_xml
#python chucky.py -n 25 --interactive -i callee atoi
python chucky.py -n 10 -i callee atoi
