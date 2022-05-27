# This module is for defining constants
from enum import Enum

DEBUG = False

OUT_DIR = "local_out"
TIMEOUT = 100

class ExitCond (Enum) :
    TIMEOUT = 0
    CRASH = 0