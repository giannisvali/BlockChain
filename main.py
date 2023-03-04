import requests
from flask import Flask, request
from argparse import ArgumentParser
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

# def positive_int(value):
#     ivalue = int(value)
#     if ivalue <= 0:
#         raise argparse.ArgumentTypeError("%s is not a positive integer" % value)
#     return ivalue

if __name__ == '__main__':
    #app.run(debug=True)

    parser = ArgumentParser()
    parser.add_argument('--ip', default='127.0.0.1')
    parser.add_argument('--port', default=5000, type=int)
    parser.add_argument('--bootstrap_ip', default='127.0.0.1', type=int)
    parser.add_argument('--bootstrap_port', default=5000, type=int)
    parser.add_argument('--is_bootstrap', type=int, choices=[0, 1], default = 0)
    #parser.add_argument('--capacity', default=5000, type=positive_int)
    parser.add_argument('--capacity', default=5000, type=int)

    # parser.add_argument('--port', default=5000, type=int)
    # parser.add_argument('--port', default=5000, type=int)

    args = parser.parse_args()
    if args.capacity <= 0:
        print('Capacity must be a positive integer! Continuing with the default value of 5.')




    args = parser.parse_args()
    port = args.port
    print(port)