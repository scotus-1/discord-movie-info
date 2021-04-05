import json
import threading


class Router:
    def __init__(self):
        self.command_dictionary = dict()
        self.kwargs_dictionary = dict()


    def register_command(self, func, command_name):
        self.command_dictionary[command_name] = func


    def register_kwargs(self, func, command_name):
        self.kwargs_dictionary[command_name] = func


    def run(self, request):
        request = json.loads(request.data)
        name = request['name']
        kwargs_command = self.kwargs_dictionary[name]

        if kwargs_command is not None:
            kwargs = kwargs_command(request)
        else:
            kwargs = None

        thread = threading.Thread(target=self.command_dictionary[name],
                                  kwargs=kwargs)

        thread.start()

