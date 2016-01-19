#!/usr/bin/env python

import os
import sys
tool_dir = os.path.dirname(os.path.realpath(__file__))
api_root = os.path.join(tool_dir, '..')
if os.path.isdir(os.path.join(api_root, 'mintapi')):
    sys.path.append(api_root)
    import mintapi
else:
    import mintapi

if __name__ == '__main__':
    mintapi.main()
