import os
import re
import math
from json import dumps, loads
from yaml import safe_load as boolean
from .time_operations import parse_time
from .regex_operations import substr


def evaluate_injection(expression: str, **kwargs):
    for attr in kwargs:
        vars()[attr] = kwargs[attr]
    return eval(expression)
