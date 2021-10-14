import pytest
from qservice import create_service


def test_default_return():
    """Should return structured namespace"""

    srv = create_service(db='database')


    @srv()
    def myservice(ctx):
        return ctx.g.db


    assert myservice().value == 'database'
    assert hasattr(myservice(), 'ok')
    assert hasattr(myservice(), 'value')
    assert hasattr(myservice(), 'errors')
    assert hasattr(myservice(), 'messages')
    assert callable(myservice().json)
    assert callable(myservice().dict)


