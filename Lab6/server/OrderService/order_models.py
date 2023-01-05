# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

class Order:
    key=''
    def __init__(self, orderId, orderName, orderCreated, orderStatus, orderProducts):
        self.orderId = orderId
        self.orderName = orderName
        self.orderCreated = orderCreated
        self.orderStatus = orderStatus
        self.orderProducts = orderProducts



