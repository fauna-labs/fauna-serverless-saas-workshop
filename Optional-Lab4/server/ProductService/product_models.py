# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

class Product:
    key =''
    def __init__(self, productId, sku, name, description, price, quantity, backorderedLimit, backordered):
        self.productId = productId
        self.sku = sku
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity
        self.backorderedLimit = backorderedLimit
        self.backordered = backordered
                

        

               

        
