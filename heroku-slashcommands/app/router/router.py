import json
import threading


command_dictionary = dict()
kwargs_dictionary = dict()


def register_command(command_name):
    def inner(func):
        command_dictionary[command_name] = func
        return func
    return inner


def register_kwargs(command_name):
    def inner(func):
        kwargs_dictionary[command_name] = func
        return func
    return inner


def run(request):
    request = json.loads(request.data)
    name = request['data']['name']
    kwargs_command = kwargs_dictionary[name]

    if kwargs_command is not None:
        kwargs = kwargs_command(request)
    else:
        kwargs = None

    thread = threading.Thread(target=command_dictionary[name],
                              kwargs=kwargs)

    thread.start()
