# qservice

Standardize methods and create step-by-step flows

## Instalation

```python
pip install qservice
```

## Basic Usage:

Using with basic validation and messages

```python

from qservice import service

@service()
def accept_only_number_two(ctx, number):
    if number != 2:
        ctx.add_error('number', 'This number is not two', True)

    ctx.add_message('This number is two')

    return number

# Using service

result = accept_only_number_two(2)
result.ok       # True
result.value    # 2
result.errors   # []
result.messages # ['This number is two']
result.json()   # return a json
resturn.dict()  # return a dict


result = accept_only_number_two(1)
result.ok       # False
result.value    # None
result.errors   # ['This number is not two']
result.messages # []
```

## Advanced usage:

For a flow, with many services , we can write steps and control your behavior.

```python

@service()
def step1(number, ctx):
    if number < 0:
        ctx.add_error('number', 'The number should be greatter then zero', True)

    return number + 1

@service()
def step2(previous_step):
    return last_step.value + 2


@service()
def step3(ctx, previous_step):
    ctx.add_message('Finsh step3')
    return previous_step.value + 1


@service()
def main_flow(ctx, dict_args):

    ctx.set_step_args(dict_args)

    ctx.add_step(step1)\
        .when(lambda v: v > 3, 'step3')

    ctx.add_step(step2)

    ctx.add_step(step3)

    return ctx.step()


if __name__ == '__main__':

    result = main_flow(number=1)
    result.ok       # True
    result.value    # 5
    result.errors   # []
    result.messages # ['Finsh step3']

    result = main_flow(number=-1)
    result.ok       # False
    result.value    # None
    result.errors   # [{"number", "The number should be greatter then zero"}]
    result.messages # []

    result = main_flow(number=5)
    result.ok       # True
    result.value    # 7
    result.errors   # []
    result.messages # ['Finsh step3']


```

## With create_service

Add some dependencies

```python

from qservice import create_service
from database import db

service = create_service(db=db)

@service()
def accept_only_number_two(ctx, number):
    if number != 2:
        ctx.add_error('number', 'This number is not two', True)

    ctx.add_message('This number is two')

    ctx.db.query("select 2")

    return number

# Using service

result = accept_only_number_two(2)
result.ok       # True
result.value    # 2
result.errors   # []
result.messages # ['This number is two']
result.json()   # return a json
resturn.dict()  # return a dict


result = accept_only_number_two(1)
result.ok       # False
result.value    # None
result.errors   # ['This number is not two']
result.messages # []
```

# Runing Tests

In root folder

```shell
pytest
```
