# Copyright Fauna, Inc.
# SPDX-License-Identifier: MIT-0

from aws_lambda_powertools import Logger
logger = Logger()

"""Log info messages
"""
def info(log_message):
    logger.info (log_message)

"""Log error messages
"""
def error(log_message):
    logger.error (log_message)
