#!/usr/bin/env python3

from glooey.helpers import *

class UpdateLogger(HoldUpdatesMixin):

    def __init__(self, hold_updates=False):
        HoldUpdatesMixin.__init__(self, hold_updates)
        self.update_log = ''

    @update_function
    def update_1(self):
        self.update_log += '1'
        
    @update_function
    def update_2(self):
        self.update_log += '2'

    @update_function
    def update_n(self, n):
        self.update_log += str(n)

            


def test_basic_usage():
    ex = UpdateLogger()
    assert ex.update_log == ''

    ex.update_1()
    assert ex.update_log == '1'

    with ex.hold_updates():
        ex.update_1()
        assert ex.update_log == '1'

    assert ex.update_log == '11'

def test_squash_multiple_updates():
    ex = UpdateLogger()
    assert ex.update_log == ''

    ex.update_1()
    ex.update_1()
    assert ex.update_log == '11'

    with ex.hold_updates():
        ex.update_1()
        ex.update_1()
        assert ex.update_log == '11'

    assert ex.update_log == '111'

def test_update_with_args():
    ex = UpdateLogger()
    assert ex.update_log == ''

    ex.update_n(3)
    assert ex.update_log == '3'

    with ex.hold_updates():
        ex.update_n(4)
        ex.update_n(5)
        ex.update_n(4)
        ex.update_n(5)
        assert ex.update_log == '3'

    assert ex.update_log == '345'

def test_update_order():
    ex = UpdateLogger()
    assert ex.update_log == ''

    ex.update_1()
    ex.update_2()
    assert ex.update_log == '12'

    with ex.hold_updates():
        ex.update_1()
        ex.update_2()
        assert ex.update_log == '12'
    assert ex.update_log == '1212'

    with ex.hold_updates():
        ex.update_2()
        ex.update_1()
        assert ex.update_log == '1212'
    assert ex.update_log == '121221'

    with ex.hold_updates():
        ex.update_n(5)
        ex.update_n(3)
        ex.update_n(4)
        ex.update_n(5)
        assert ex.update_log == '121221'
    assert ex.update_log == '121221345'

def test_no_update_needed():
    ex = UpdateLogger()
    assert ex.update_log == ''

    ex.update_1()
    assert ex.update_log == '1'

    ex.update_2()
    assert ex.update_log == '12'

    with ex.hold_updates():
        pass
    assert ex.update_log == '12'

    with ex.hold_updates():
        ex.update_1()
        assert ex.update_log == '12'
    assert ex.update_log == '121'

    with ex.hold_updates():
        ex.update_2()
        assert ex.update_log == '121'
    assert ex.update_log == '1212'

def test_apply_hold_in_ctor():
    ex = UpdateLogger(hold_updates=True)
    assert ex.update_log == ''

    ex.update_1()
    assert ex.update_log == ''

    ex.resume_updates()
    assert ex.update_log == '1'

def test_nested_holds():
    ex = UpdateLogger()
    assert ex.update_log == ''

    with ex.hold_updates():
        with ex.hold_updates():
            ex.update_1()
            assert ex.update_log == ''
        ex.update_2()
        assert ex.update_log == ''
    assert ex.update_log == '12'



