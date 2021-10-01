import pytest
from qservice import service


def test_default_return():
    """Should return structured namespace"""

    @service()
    def myservice():
        return 'ok'

    assert myservice().value == 'ok'
    assert hasattr(myservice(), 'ok')
    assert hasattr(myservice(), 'value')
    assert hasattr(myservice(), 'errors')
    assert hasattr(myservice(), 'messages')
    assert callable(myservice().json)
    assert callable(myservice().dict)


def test_messages():
    """Should return messages in returned object"""

    @service()
    def myservice(fn):
        fn.add_message('the field message')
        return 'ok'

    assert myservice().value == 'ok'
    assert len(myservice().messages) == 1
    assert myservice().messages[0] == 'the field message'


def test_errors():
    """Should return messages in returned object"""

    @service()
    def myservice(fn):
        fn.add_error('field','the field error')
        return 'ok'

    assert myservice().ok == False
    assert myservice().value == 'ok'
    assert len(myservice().errors) == 1
    assert myservice().errors['field'] == 'the field error'


    @service()
    def myservice2(fn):
        fn.add_error('field','the field error')
        fn.add_error('field2','the field2 error')
        fn.validate()
        return 'ok'

    assert myservice2().ok is False
    assert myservice2().value is None
    assert len(myservice2().errors) == 2
    assert myservice2().errors['field'] == 'the field error'


    @service()
    def myservice3(fn):
        fn.add_error('field','the field error', True)
        fn.add_error('field2','the field2 error', True)
        return 'ok'

    assert myservice3().ok is False
    assert myservice3().value is  None
    assert len(myservice3().errors) is 1
    assert myservice3().errors['field'] == 'the field error'

def test_return_dict():
    """Should return messages in returned object"""

    @service()
    def myservice():
        return 'ok'

    _dict = myservice().dict
    assert callable(_dict)
    assert _dict().get('ok')
    assert _dict().get('value') == 'ok'
    assert _dict().get('errors') == {}
    assert _dict().get('messages') == []


def test_return_json():
    """Should return messages in returned object"""

    @service()
    def myservice():
        return 'ok'
    _json = myservice().json
    assert callable(_json)
    assert _json() == '{"ok": true, "errors": {}, "messages": [], "value": "ok"}'


def test_exception():

    @service(raise_exceptions=False)
    def myservice():
        x= 1/0
        return 'ok'

    assert myservice().value is None
    assert myservice().ok is False
    assert len(myservice().errors) == 1
    assert myservice().errors['exception'] == 'division by zero'

    @service(raise_exceptions=True)
    def myservice():
        x= 1/0
        return 'ok'

    with pytest.raises(Exception):
        myservice()



def test_context_name():

    @service(context_varname='ctx')
    def myservice(ctx):
        ctx.add_message('context')
        return 'ok'

    result = myservice()
    assert result.ok is True
    assert len(result.messages) == 1

    @service(context_varname='jj')
    def myservice(jj):
        jj.add_message('context')
        return 'ok'

    result = myservice()
    assert result.ok is True
    assert len(result.messages) == 1



def test_add_step():
    """Flow: should add step to execute service flow"""

    @service()
    def step1(number, **kwargs):
        return number

    @service()
    def step2(number, steps, previous_step, **kwargs):
        return 2 * number



    @service(context_varname='ctx')
    def myflow(ctx, **kwargs):
        ctx.set_step_args(kwargs)

        ctx.add_step(step1)

        ctx.add_step(step2)

        return ctx.step()


    result = myflow(number=2)
    assert result.ok
    assert result.value == 4


def test_step_errors_and_messages():
    """steps: should execute up to first service error.
    Service `step3` should not be executed
    """

    @service()
    def step1(fn, number, **kwargs):
        fn.add_message("number is {}".format(number))

        return 1 + number

    @service()
    def step2(fn, number, steps, previous_step, **kwargs):
        fn.add_message("step 2")
        fn.add_error('number', 'Number shoud be {}', True)
        return 2 * previous_step.value


    @service()
    def step3(number, steps, previous_step):
        return previous_step.value + 1


    @service(context_varname='ctx')
    def myflow(ctx, number):
        ctx.set_step_args(dict(number=number))

        ctx.add_step(step1)

        ctx.add_step(step2)

        ctx.add_step(step3)

        return ctx.step()


    result = myflow(number=2)
    assert result.ok == False
    assert result.value == None
    assert len(result.messages) == 2
    assert len(result.errors) == 1



def test_step_when():
    """steps: should be executed with conditional roles.
    """

    @service()
    def step1(fn, number, **kwargs):
        return number

    @service()
    def step2(fn, number, steps, previous_step, **kwargs):
        return 2 * previous_step.value


    @service()
    def step3(number, steps, previous_step, **kwargs):
        return previous_step.value + 1

    @service()
    def step4(steps, previous_step, **kwargs):
        return previous_step.value + 10


    @service(context_varname='ctx')
    def myflow(ctx, **kwargs):
        ctx.set_step_args(kwargs)

        ctx.add_step(step1)\
            .when(lambda v: v == 2, then=step3)\
            .when(lambda v: v == 5, then='step4')

        ctx.add_step(step2)

        ctx.add_step(step3)

        ctx.add_step(step4)

        return ctx.step()

    # Casos de teste
    result = myflow(number=1)
    assert result.ok == True
    assert result.value == 13

    result = myflow(number=5)
    assert result.ok == True
    assert result.value == 15

    result = myflow(number=3)
    assert result.ok == True
    assert result.value == 17
