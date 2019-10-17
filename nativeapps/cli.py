#!/usr/bin/env python

"""
    Basic command line interface, entry point.
"""

import argparse
from . import web

def cli():
    """
        Start the service.  To stop it just hit CTRL+C.
    """

    desc = "Web server and interface to serve mobile applications."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-p', '--port',
                        help="The port where the server will listen to.",
                        default=10000)
    parser.add_argument('-v', '--verbose',
                        help="The project in which we are carrying out the merge.",
                        action='store_true')
    args = parser.parse_args()

    web.run(host="0.0.0.0",
            port=int(args.port),
            threaded=True,
            debug=args.verbose)

if __name__ == "__main__":
    cli()
