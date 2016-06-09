# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from importlib import import_module

import pytest


@pytest.mark.parametrize('exc_name,mod_name', [
    ('OwnershipError', 'ownership'),
    ('SpoolFundsError', 'spool'),
    ('InvalidTransactionError', 'spoolex'),
    ('SpoolverbError', 'spoolverb'),
])
def test_exceptions(exc_name, mod_name):
    module = import_module('.{}'.format(mod_name), package='spool')
    ExceptionClass = getattr(module, exc_name)
    exception = ExceptionClass('error message')
    assert exception.message == 'error message', exception
    assert exception.__str__() == 'error message', exception
