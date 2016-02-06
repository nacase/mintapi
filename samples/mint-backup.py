#!/usr/bin/env python

import json
import time
import os
import sys
tool_dir = os.path.dirname(os.path.realpath(__file__))
api_root = os.path.join(tool_dir, '..')
if os.path.isdir(os.path.join(api_root, 'mintapi')):
    sys.path.append(api_root)
    import mintapi
else:
    import mintapi

def info(msg):
    print('-> {msg:s}'.format(msg=msg))

def main(argv):
    import getpass
    import argparse

    try:
        import keyring
    except ImportError:
        keyring = None

    # Parse command-line arguments {{{
    cmdline = argparse.ArgumentParser()
    cmdline.add_argument('email', nargs='?', default=None,
                         help='The e-mail address for your Mint.com account')
    cmdline.add_argument('password', nargs='?', default=None,
                         help='The password for your Mint.com account')
    cmdline.add_argument('--filename', '-f', help='write results to file. can '
                         'be {csv,json} format. default is to write to '
                         'stdout.')
    cmdline.add_argument('--keyring', action='store_true',
                         help='Use OS keyring for storing password '
                         'information')

    options = cmdline.parse_args(argv)

    if options.keyring and not keyring:
        cmdline.error('--keyring can only be used if the `keyring` '
                      'library is installed.')

    if sys.version_info[0] == 2:
        from __builtin__ import raw_input as input
    else:
        # Seems like this shouldn't be necessary, but without this
        # the interpreter was treating 'input' as a local variable
        # in its first pass and throwing UnboundLocalError when calling
        # input()
        from builtins import input

    # Try to get the e-mail and password from the arguments
    email = options.email
    password = options.password

    if not email:
        # If the user did not provide an e-mail, prompt for it
        email = input("Mint e-mail: ")

    if keyring and not password:
        # If the keyring module is installed and we don't yet have
        # a password, try prompting for it
        password = keyring.get_password('mintapi', email)

    if not password:
        # If we still don't have a password, prompt for it
        password = getpass.getpass("Mint password: ")

    if options.keyring:
        # If keyring option is specified, save the password in the keyring
        keyring.set_password('mintapi', email, password)

    info('Logging in')
    mint = mintapi.Mint.create(email, password, debug=False)

    data = {}

    info('Fetching account information')
    data['accounts'] = mintapi.api.make_accounts_presentable(
            mint.get_accounts(get_detail=False)
    )

    info('Downloading all transactions')
    txn_data = mint.get_transactions_json(include_investment=True,
                                          skip_duplicates=True,
                                          start_date=None)
    data['transactions'] = txn_data

    info('Fetching historical stats')
    data['net_worth'] = mint.get_net_worth()
    data['tags'] = mint.get_tags()

    nw_trends = mint.get_trends_history('NW')
    #print('networth trends: ' + str(nw_trends))
    data['nw_trends'] = nw_trends

    fname = 'mint-backup-{ts:s}.json'.format(ts=time.strftime('%Y%m%d-%H%M%S'))
    info('Saving data to {fname:s}'.format(fname=fname))
    with open(fname, 'w+') as f:
        json.dump(data, f, indent=2)

if __name__ == '__main__':
    main(sys.argv[1:])
