from collections import namedtuple
from functools import wraps
import inspect
import json


def create_service(**deps):
    return __service(**deps)


def service(**kw):
    return __service()(**kw)


def __service(**deps):
    def decorator(raise_exceptions=True, stop_on_error=True, context_varname='ctx', steps_varname='steps', previous_step_varname='previous_step', global_varname='g'):
        def wrapper(func):
            @wraps(func)
            def wrapper(**kwargs):
                """A wrapper function"""
                class Context():
                    def __init__(self, _stop_on_error):
                        self.ok = None
                        self.name = None
                        self.value = None
                        self.messages = []
                        self.errors = {}
                        self.steps = []
                        self.conditions = []
                        self.step_args = {}
                        self._last_added_step = ''
                        self._stop_on_error = _stop_on_error

                    def add_message(self, msg):
                        self.messages.append(msg)

                    def add_error(self, field, message, stop_on_error=False):
                        self.errors[field] = message
                        if self._stop_on_error or stop_on_error:
                            raise ValueError()

                    def validate(self):
                        if len(self.errors) > 0:
                            raise ValueError()

                    def to_dict(self):
                        data = {}
                        data["ok"] = self.ok
                        data["errors"] = self.errors
                        data["messages"] = self.messages
                        data["value"] = self.value
                        return data

                    def to_json(self):
                        return json.dumps(self.to_dict())

                    def set_step_args(self, kwargs: dict):
                        self.step_args = kwargs

                    def add_step(self, fn_service):
                        """Using by flow execution"""
                        self.steps.append(fn_service)
                        self._last_added_step = fn_service.__name__
                        return self


                    def when(self, cb, then):
                        then_name=then
                        if callable(then):
                            then_name = then.__name__
                        self.conditions.append((self._last_added_step, cb, then_name))
                        return self


                    def step(self):
                        self.step_args['steps'] = {}
                        self.step_args['last_step'] = None
                        next_step = None

                        for fn in self.steps:
                            name = fn.__name__

                            if next_step and next_step != name:
                                continue

                            result = fn(**self.step_args)

                            self.messages.extend(result.messages)

                            if not result.ok:
                                self.errors.update(result.errors)
                                return result.value

                            next_step = None
                            for _, cb, then in self._get_conditions_for(name):
                                if cb(result.value):
                                    next_step = then
                                    break

                            self.step_args[previous_step_varname] = result
                            self.step_args[steps_varname][name] = result

                        return result.value


                    def _get_conditions_for(self, name):
                        return list(filter(lambda condition: condition[0]==name, self.conditions))

                    def _get_declared_args(self, func, kwargs):
                        parameters = inspect.signature(func).parameters
                        varkw = inspect.getfullargspec(func).varkw

                        if varkw:
                            return kwargs

                        declared_args = {}
                        for k, v in kwargs.items():
                            if parameters.get(k):
                                declared_args[k] = v

                        return declared_args


                context = Context(_stop_on_error=stop_on_error)
                Result = namedtuple("Result", "ok name value errors messages json dict")
                GlobalVar = namedtuple("GlobalVar", deps.keys())

                try:
                    setattr(context, global_varname, GlobalVar(**deps))
                    kwargs[context_varname] = context
                    context.name = func.__name__
                    context.value = func(**context._get_declared_args(func, kwargs))

                except ValueError as ve:
                    pass
                except Exception as ex:
                    if raise_exceptions:
                        raise ex
                    context.errors["exception"] = str(ex)

                context.ok = len(context.errors) == 0

                return Result(ok=context.ok, name=context.name, value=context.value, errors=context.errors, messages=context.messages, json=context.to_json, dict=context.to_dict)

            return wrapper
        return wrapper
    return decorator
