import json
import importlib
import threading


class Router:
    def __init__(self, package_name):
        self.command_dictionary = dict()
        self.kwargs_dictionary = dict()
        importlib.__import__(package_name.split(".")[0])


    def register_command(self, func, command_name):
        print(command_name)
        self.command_dictionary[command_name] = func


    def register_kwargs(self, func, command_name):
        print(command_name)
        self.kwargs_dictionary[command_name] = func


    def run(self, request):
        request = json.loads(request.data)
        name = request['data']['name']
        print(self.kwargs_dictionary)
        print(self.command_dictionary)
        kwargs_command = self.kwargs_dictionary[name]

        if kwargs_command is not None:
            kwargs = kwargs_command(request)
        else:
            kwargs = None

        thread = threading.Thread(target=self.command_dictionary[name],
                                  kwargs=kwargs)

        thread.start()

