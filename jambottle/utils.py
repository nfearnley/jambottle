from itertools import islice


# https://stackoverflow.com/questions/3992735/python-generator-that-groups-another-iterable-into-groups-of-n/3992765
# https://stackoverflow.com/questions/31164731/python-chunking-csv-file-multiproccessing/31170795#31170795
# https://docs.python.org/3/library/functions.html#iter
def grouper(iterable, n):
    """
    >>> list(grouper(3, 'ABCDEFG'))
    [['A', 'B', 'C'], ['D', 'E', 'F'], ['G']]
    """
    iterable = iter(iterable)
    return iter(lambda: list(islice(iterable, n)), [])
