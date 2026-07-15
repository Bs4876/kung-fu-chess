from user_input.mapper_proxy import MapperProxy


class FakeMapper:
    def __init__(self, label):
        self.label = label

    def pixel_to_cell(self, x, y):
        return (self.label, x, y)


def test_delegates_to_the_initial_mapper():
    proxy = MapperProxy(FakeMapper("first"))
    assert proxy.pixel_to_cell(10, 20) == ("first", 10, 20)


def test_replace_swaps_the_delegate_for_subsequent_calls():
    proxy = MapperProxy(FakeMapper("first"))
    proxy.replace(FakeMapper("second"))
    assert proxy.pixel_to_cell(10, 20) == ("second", 10, 20)
