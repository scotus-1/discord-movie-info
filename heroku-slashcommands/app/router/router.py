import json
import threading


class Router:
    def __init__(self):
        self.command_dictionary = dict()
        self.kwargs_dictionary = dict()


    def register_command(self, command_name):
        def inner(func):
            print(command_name)
            self.command_dictionary[command_name] = func
            return func
        return inner

    def register_kwargs(self, command_name):
        def inner(func):
            print(command_name)
            self.kwargs_dictionary[command_name] = func
            return func
        return inner

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

