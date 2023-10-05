import logging

from products.exceptions import NotFound
from nameko.events import event_handler
from nameko.rpc import rpc

from products import dependencies, schemas


logger = logging.getLogger(__name__)


class ProductsService:

    name = 'products'

    storage = dependencies.Storage()

    @rpc
    def get(self, product_id):
        product = self.storage.get(product_id)
        if not product:
            raise NotFound('Product with id {} not found'.format(product_id))

        return schemas.Product().dump(product).data

    @rpc
    def list(self):
        products = self.storage.list()

        return schemas.Product(many=True).dump(products).data
    
    @rpc
    def get_all_products(self):
        products = self.list()
        if not products:
            raise NotFound('Any products was found')
        
        return products

    @rpc
    def create(self, product):
        product = schemas.Product(strict=True).load(product).data
        self.storage.create(product)

    @rpc
    def remove(self, product_id):
        product = self.storage.get(product_id)
        if not product:
            raise NotFound('Product with id {} not found'.format(product_id))

        self.storage.delete(product['id'])

    @event_handler('orders', 'order_created')
    def handle_order_created(self, payload):
        for product in payload['order']['order_details']:
            self.storage.decrement_stock(
                product['product_id'], product['quantity'])
            
    @event_handler('orders', 'order_deleted')
    def handle_order_deleted(self, payload):
        for product in payload['order']['order_details']:
            self.storage.increment_stock(
                product['product_id'], product['quantity'])
