#!/bin/bash

# DIR="${BASH_SOURCE%/*}"
# if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
# . "$DIR/nex-include.sh"

# to ensure if 1 command fails.. build fail
set -e

# ensure prefix is pass in
if [ $# -lt 1 ] ; then
	echo "NEX smoketest needs prefix"
	echo "nex-smoketest.sh acceptance"
	exit
fi

PREFIX=$1

# check if doing local smoke test
if [ "${PREFIX}" != "local" ]; then
    echo "Remote Smoke Test in CF"
    STD_APP_URL=${PREFIX}
else
    echo "Local Smoke Test"
    STD_APP_URL=http://localhost:8000
fi

echo STD_APP_URL=${STD_APP_URL}

# Test: Create Products
echo "=== Creating a product id: the_odyssey ==="
curl -s -XPOST  "${STD_APP_URL}/products" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{"id": "the_odyssey", "title": "The Odyssey", "passenger_capacity": 101, "maximum_speed": 5, "in_stock": 10}'
echo

echo "=== Creating a product id: the_enigma ==="
curl -s -XPOST  "${STD_APP_URL}/products" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{"id": "the_enigma", "title": "The Enigma", "passenger_capacity": 80, "maximum_speed": 4, "in_stock": 15}'
echo
# Test: Get Product
echo "=== Getting product id: the_odyssey ==="
curl -s "${STD_APP_URL}/products/the_odyssey" | jq .

echo "=== Getting product id: the_enigma ==="
curl -s "${STD_APP_URL}/products/the_enigma" | jq .

#Test: Listing All Products
echo "=== Listing all Products ==="
curl -s "${STD_APP_URL}/products" | jq .

# Test: Create Order
echo "=== Creating Order ==="
FIRST_ORDER_ID=$(
    curl -s -XPOST "${STD_APP_URL}/orders" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{"order_details": [{"product_id": "the_odyssey", "price": "100000.99", "quantity": 1}]}' 
)
echo ${FIRST_ORDER_ID}
FIRST_ID=$(echo ${FIRST_ORDER_ID} | jq '.id')
SECOND_ORDER_ID=$(
    curl -s -XPOST "${STD_APP_URL}/orders" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{"order_details": [{"product_id": "the_odyssey", "price": "100000.99", "quantity": 4}, {"product_id": "the_enigma", "price": "10000.99", "quantity": 5}]}' 
)
echo ${SECOND_ORDER_ID}
SECOND_ID=$(echo ${SECOND_ORDER_ID} | jq '.id')

# Test: Get Order back
echo "=== Getting Order ==="
curl -s "${STD_APP_URL}/orders/${FIRST_ID}" | jq .
curl -s "${STD_APP_URL}/orders/${SECOND_ID}" | jq .

# Test: Delete Order
echo "=== Deleting Order ==="
curl -s -XDELETE "${STD_APP_URL}/orders/${FIRST_ID}"
echo "Deleted order id ${FIRST_ID}"
curl -s -XDELETE "${STD_APP_URL}/orders/${SECOND_ID}"
echo "Deleted order id ${SECOND_ID}"

#Test: Delete Product
echo "=== Deleting Products ==="
curl -s -XDELETE "${STD_APP_URL}/products/the_odyssey"
echo "Deleted order id the_odyssey"
curl -s -XDELETE "${STD_APP_URL}/products/the_enigma"
echo "Deleted order id the_enigma"

echo "=== End of the tests ==="