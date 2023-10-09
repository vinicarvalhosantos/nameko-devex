from os import name
from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from typing import List
from gateapi.api import schemas
from gateapi.api.dependencies import get_rpc, config
from .exceptions import OrderNotFound
from fastapi import Response

router = APIRouter(
    prefix = "/orders",
    tags = ['Orders']
)

@router.get("/{order_id}", status_code=status.HTTP_200_OK)
def get_order(order_id: int, rpc = Depends(get_rpc)):
    try:
        return _get_order(order_id, rpc)
    except OrderNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )

@router.get("", status_code=status.HTTP_200_OK)
def get_all_orders(rpc = Depends(get_rpc)):
    try:
        with rpc.next() as nameko_rpc:
            orders = nameko_rpc.orders.list_all_orders()
            for order in orders:
                order = __format_order(order)

            return order
    except OrderNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )

def _get_order(order_id, nameko_rpc):
    # Retrieve order data from the orders service.
    # Note - this may raise a remote exception that has been mapped to
    # raise``OrderNotFound``
    with nameko_rpc.next() as nameko:
        order = nameko.orders.get_order(order_id)

        order = __format_order(order)

    return order

@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.CreateOrderSuccess)
def create_order(request: schemas.CreateOrder, rpc = Depends(get_rpc)):
    id_ =  _create_order(request.dict(), rpc)
    return {
        'id': id_
    }

def _create_order(order_data, nameko_rpc):
    # check order product ids are valid
    with nameko_rpc.next() as nameko:
        products_list = nameko.products.list()
        valid_product_ids = []
        product = {}

        for product_temp in products_list:
            valid_product_ids.append(product_temp['id'])
            product[product_temp['id']] = product_temp

        for item in order_data['order_details']:
            product_id = item['product_id']
            if product_id not in valid_product_ids:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Product with id {item['product_id']} not found")
            
            __check_product_stock(product[product_id], item['quantity'])

        valid_product_ids = {prod['id'] for prod in nameko.products.list()}
        for item in order_data['order_details']:
            if item['product_id'] not in valid_product_ids:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Product with id {item['product_id']} not found"
            )
        # Call orders-service to create the order.
        result = nameko.orders.create_order(
            order_data['order_details']
        )
        return result['id']
    
def __check_product_stock(product, order_quantity):
    product_stock = product['in_stock']
    if product_stock == 0 or order_quantity > product_stock:
        raise HTTPException( status_code= status.HTTP_404_NOT_FOUND, detail='No available stock for this product id \'{}\''.format(product['id']))
    

def __format_order(order):
    # get the configured image root
    image_root = config['PRODUCT_IMAGE_ROOT']

    # Enhance order details with product and image details.
    for item in order['order_details']:
        product_id = item['product_id']
            
        # Construct an image url.
        item['image'] = '{}/{}.jpg'.format(image_root, product_id)
    return order  

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, rpc = Depends(get_rpc)):
    try:
        with rpc.next() as nameko_rpc:
            nameko_rpc.orders.delete_order(order_id)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    except OrderNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        ) 