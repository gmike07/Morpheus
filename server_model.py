import json
import time
import numpy as np
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
from threading import Thread, Event, Lock
import sys
from models.model_creator import create_model
from models.ae_trainer import train_ae
from models.rl_trainer import train_rl
from models.dnn_trainer import train_dnn
from config_creator import get_config, requires_helper_model, is_threaded_model
from argument_parser import parse_arguments
from contextlib import redirect_stdout, redirect_stderr
import signal
import socket
from typing import *
from queue import Queue
httpd = None


class Arguments:
    def __init__(self):
        self.other_thread = None
        self.event_thread = None
        self.model_name = None
        self.model = None
        self.logger = open('./all_logs_server_model.txt', 'w')
        self.data_recieved = [Queue() for _ in range(get_config()['num_clients'])]
        self.data_to_send = [Queue() for _ in range(get_config()['num_clients'])]
        # self.lock = Lock()
        # self.locks = [Lock() for _ in range(get_config()['num_clients'])]

    def print_redirect(self, message):
        with redirect_stdout(self.logger):
            print(message)
        self.logger.flush()
        print(message)


def signal_handler(sig, frame):
    global httpd
    if httpd is not None:
        httpd.shutdown()
    sys.exit(0)


def get_lambda_trainer(model, model_name, event, f=None):
    if model_name == 'DNNTrainer':
        return lambda: train_dnn(model, event, f=f)
    if model_name == 'AETrainer':
        return lambda: train_ae(model, event, f=f)
    if model_name in ['DRL', 'REINFORCE', 'REINFORCE_AE']:
        return lambda: train_rl(model, event)


def get_server_model(arguments):
    class HandlerClass(BaseHTTPRequestHandler):
        def default_headers(self):
            self.send_response(200, 'OK')
            self.end_headers()

        def do_GET(self):
            self.send_response(200)
            self.end_headers()

        def handle_clear(self):
            arguments.print_redirect('clearing...')
            if arguments.model is not None:
                arguments.model.clear()
            return self.default_headers()

        def handle_done(self):
            arguments.print_redirect('done...')
            if arguments.model is not None:
                arguments.model.done()
            return self.default_headers()

        def handle_test(self, is_test):
            print('testing ', is_test)
            get_config()['test'] = is_test
            return self.default_headers()

        def send_OK_and_prediction(self, prediction):
            self.default_headers()
            self.wfile.write(json.dumps({'cc': str(prediction)}).encode('utf-8'))

        def handle_state(self, parsed_data):
            parsed_data['server_id'] -= 1
            parsed_data['state'] = np.array(parsed_data['state']).reshape(1, -1)
            print('predicting server', parsed_data['server_id'], end=' ')
            arguments.model.update(parsed_data)
            prediction = arguments.model.predict(parsed_data)
            print('prediction is', prediction)
            self.send_OK_and_prediction(prediction)

        def handle_stateless(self, parsed_data):
            parsed_data['server_id'] -= 1
            print('predicting server', parsed_data['server_id'], end=' ')
            prediction = arguments.model.predict(parsed_data)
            print('prediction is', prediction)
            self.send_OK_and_prediction(prediction)


        def handle_switch(self, parsed_data):
            arguments.print_redirect(f"switching to model {parsed_data['model_name']} and load: {parsed_data['load']}")
            if arguments.model_name == parsed_data['model_name'] and parsed_data['model_name'] != 'stackingModel':
                if requires_helper_model(arguments.model_name):
                    with redirect_stdout(arguments.logger):
                        arguments.model.update_helper_model(create_model(get_config()['num_clients'], parsed_data['helper_model']))
                    arguments.logger.flush()
                return self.default_headers()
            get_config()['batch_size'] = 1
            if arguments.model is not None:
                if arguments.event_thread is not None:
                    arguments.event_thread.set()
                arguments.model.save()
            
            arguments.model, arguments.other_thread, arguments.event_thread = None, None, None
            if len(parsed_data['models']) != 0:
                get_config()['models'] = parsed_data['models']
            with redirect_stdout(arguments.logger):
                arguments.model = create_model(get_config()['num_clients'], parsed_data['model_name'], parsed_data['helper_model'])
            arguments.logger.flush()
            if parsed_data['load'] is True:
                arguments.model.load()
            elif not get_config()['test'] and is_threaded_model(parsed_data['model_name']):
                arguments.event_thread = Event()
                arguments.other_thread = Thread(target=get_lambda_trainer(arguments.model, parsed_data['model_name'], arguments.event_thread, arguments.logger))
                arguments.other_thread.start()
            arguments.model_name = parsed_data['model_name']
            return self.default_headers()

        def hanlde_message(self, parsed_data):
            if parsed_data['message'] == 'sock finished':
                print('server', parsed_data['server_id'] - 1, 'finished')

        def do_POST(self):
            try:
                content_len = int(self.headers.get('Content-Length'))
                data = self.rfile.read(content_len)
                parsed_data = json.loads(data)
                if 'state' in parsed_data:
                    self.handle_state(parsed_data)
                elif 'stateless' in parsed_data:
                    self.handle_stateless(parsed_data)
                elif 'clear' in parsed_data:
                    self.handle_clear()
                elif 'done' in parsed_data:
                    self.handle_done()
                elif 'test' in parsed_data:
                    self.handle_test(parsed_data['test'])
                elif 'switch_model' in parsed_data:
                    self.handle_switch(parsed_data)
                elif 'message' in parsed_data:
                    self.hanlde_message(parsed_data)
                elif 'kill' in parsed_data:
                    exit()
                else:
                    print(parsed_data)
                    arguments.logger.write("400-dct is " + str(parsed_data) +'\n')
                    arguments.logger.flush()
                    self.send_response(400)
                    self.end_headers()
            except Exception as e:
                print('exception', e)
                arguments.logger.write("400-exception is " + str(e) +'\n')
                arguments.logger.flush()
                self.send_response(400, "error occurred")
                self.end_headers()
    return HandlerClass, arguments.logger, arguments


def state_handler(arguments):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)

        def handle(self) -> None:
            LEN = 1048576 # 2**20
            # self.request is the TCP socket connected to the client
            while True:
                data = bytearray()
                while len(data) < LEN:
                    recv_len = min(4096, LEN - len(data))
                    packet = self.request.recv(recv_len).strip()
                    data.extend(packet)
                if not data:
                    print('DISCONNECTED')
                    break
                try:
                    body = data.decode("utf-8").strip()
                    body = body[:body.find('\n')]
                    args = json.loads(body)
                    if 'message' in args and args['message'] == 'close socket':
                        response_str = json.dumps({'cc': '0'}) + '\n'
                        response_str = response_str.encode("utf-8")
                        response_str = response_str.ljust(100 - len(response_str), b'0')
                        self.request.sendall(response_str)
                        return
                    server_id = int(args['server_id']) - 1

                    # arguments.lock.acquire()
                    arguments.data_recieved[server_id].put(args)
                    # arguments.lock.release()

                    while True:
                        # arguments.locks[server_id].acquire()
                        if not arguments.data_to_send[server_id].empty():
                            break
                        # arguments.locks[server_id].release()
                        time.sleep(0.01)
                    response = arguments.data_to_send[server_id].get()
                    response_str = json.dumps(response) + '\n'
                    response_str = response_str.encode("utf-8")
                    response_str = response_str.ljust(100 - len(response_str), b'0'); print('response for server', server_id, 'is', response)
                    self.request.sendall(response_str)
                except Exception:
                    print('exception', traceback.format_exc())
                    print('the data is:', data.decode("utf-8").strip())
    return Handler, arguments


def handle_state(arguments, parsed_data):
    parsed_data['server_id'] -= 1
    parsed_data['state'] = np.array(parsed_data['state']).reshape(1, -1)
    print('predicting server', parsed_data['server_id'], end=' ')
    arguments.model.update(parsed_data)
    prediction = arguments.model.predict(parsed_data)
    print('prediction is', prediction)
    return  {'cc': str(prediction)}


def handle_stateless(arguments, parsed_data):
    parsed_data['server_id'] -= 1
    print('predicting server', parsed_data['server_id'], end=' ')
    prediction = arguments.model.predict(parsed_data)
    print('prediction is', prediction)
    return {'cc': str(prediction)}


def execute_commands(arguments, json_command):
    if 'state' in json_command:
        return handle_state(arguments, json_command)
    elif 'stateless' in json_command:
        return handle_stateless(arguments, json_command)


def process_states(arguments):
    while True:
        for i in range(get_config()['num_clients']):
            if not arguments.data_recieved[i].empty():
                response = execute_commands(arguments, arguments.data_recieved[i].get())
                # arguments.locks[i].acquire()
                arguments.data_to_send[i].put(response)
                # arguments.locks[i].release()



def run_server(server_handler, addr, port, server_class=HTTPServer):
    global httpd
    server_address = (addr, port)
    handler, f, args = server_handler()
    httpd = server_class(server_address, handler)
    f.write(f"Starting httpd server on {addr}:{port} with model None\n")
    f.flush()
    print(f"Starting httpd server on {addr}:{port} with model None")
    thread = Thread(target=lambda: httpd.serve_forever())
    thread.start()

    # handler to use for state parsing
    for i in range(1, get_config()['num_clients'] + 1):
        state_address = (addr, port + i)
        handler, arguments = state_handler(args)
        httpd_main = server_class(state_address, handler)
        print(f'Starting httpd server for server {i} on {addr}:{port + i} with model None')
        thread = Thread(target=lambda: httpd_main.serve_forever())
        thread.start()

    process_states(args)


if __name__ == '__main__':
    parse_arguments()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    run_server(lambda: get_server_model(Arguments()), 'localhost', get_config()['server_port'])
