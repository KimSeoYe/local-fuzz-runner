from __future__ import print_function #for python 2.7

import os
import re
import sys
import random
import string
import shutil

import fuzzUtils as utils

if len(sys.argv) != 4:
    print("usage: python fuzzLocal.py [dirpath_for_git] [origin_seed_dir] [per_func_seed_dir]")
    sys.exit()

path_for_git = os.path.realpath(sys.argv[1])
origin_seed_dir = os.path.realpath(sys.argv[2])
per_func_seed_dir = os.path.realpath(sys.argv[3])

changed_funcs = utils.get_changed_func_names(path_for_git)
local_seeddir_path = utils.get_seeds_for_local_mode(origin_seed_dir, per_func_seed_dir, changed_funcs)
print(local_seeddir_path)

# TMP
shutil.rmtree(local_seeddir_path)