#!/usr/bin/env python3

from glooey.helpers import *

class UpdateLogger(HoldUpdatesMixin):

    def __init__(self):
        super().__init__()
        self.update_log = ''

    @update_function(1)
    def update_1(self):
        self.update_log += '1'
        
    @update_function(2)
    def update_2(self):
        self.update_log += '2'
            



def test_basic_usage():
    ex = UpdateLogger()
    assert ex.update_log == ''

    ex.update_1()
    assert ex.update_log == '1'

    with ex.hold_updates():
        ex.update_1()
        assert ex.update_log == '1'

    assert ex.update_log == '11'

def test_update_order():
    # This isn't a great test, because even is the order is random, there's a 
    # reasonable chance it'll pass.
    ex = UpdateLogger()
    assert ex.update_log == ''

    ex.update_1()
    assert ex.update_log == '1'

    ex.update_2()
    assert ex.update_log == '12'

    with ex.hold_updates():
        ex.update_2()
        assert ex.update_log == '12'

        ex.update_1()
        assert ex.update_log == '12'

    assert ex.update_log == '1212'

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

