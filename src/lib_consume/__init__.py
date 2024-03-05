

def consume(iterable) -> None:
    # while True:
    #     try:
    #         next(iterable)
    #     except StopIteration:
    #         break
    for _ in iterable: pass


def _add_one(input:list):
    input[0] += 1


def test_consume():
    iterable = [[1], [2], [3]]
    consume(
        map(
            _add_one,
            iterable,
        )
    )
    expected = [[2], [3], [4]]
    assert iterable == expected


if __name__ == '__main__':
    test_consume()
