#!/bin/bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

csv=$(find *.csv)
echo $csv
python3 client_order.py -i "$csv"