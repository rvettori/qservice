from collections import namedtuple
from functools import wraps
import json


def service(raise_exceptions=False):
    def wrapper(func):
        @wraps(func)
        def wrapper(**kwargs):
            """A wrapper function"""
            ok = None
            value = None
            messages = []
            errors = {}

            def add_message(msg):
                messages.append(msg)

            def add_error(field, message, stop_execution=False):
                errors[field] = message
                if stop_execution:
                    raise ValueError()

            def validate():
                if len(errors) > 0:
                    raise ValueError()

            def to_dict():
                data = {}
                data["ok"] = ok
                data["errors"] = errors
                data["messages"] = messages
                data["value"] = value
                return data

            def to_json():
                return json.dumps(to_dict())

            Fn = namedtuple("fn", "add_message add_error validate")
            Result = namedtuple("Result", "ok value errors messages json dict")

            try:
                if func.__code__.co_argcount > 0:
                    kwargs["fn"] = Fn(add_message, add_error, validate)

                value = func(**kwargs)

            except ValueError as ve:
                pass
            except Exception as ex:
                if raise_exceptions:
                    raise ex
                errors["exception"] = str(ex)

            ok = len(errors) == 0
            return Result(ok=ok, value=value, errors=errors, messages=messages, json=to_json, dict=to_dict)

        return wrapper
    return wrapper
