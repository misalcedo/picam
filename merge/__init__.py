def merge_dict(a, b):
    """Deep-merges dictionaries."""

    return dict(dict_merger(a, b))


def dict_merger(a, b):
    """See https://stackoverflow.com/questions/7204805/dictionaries-of-dictionaries-merge"""
    for k in set(a.keys()).union(b.keys()):
        if k in a and k in b:
            if isinstance(a[k], dict) and isinstance(b[k], dict):
                yield (k, dict(merge_dict(a[k], b[k])))
            else:
                # If one of the values is not a dict, you can't continue merging it.
                # Value from second dict overrides one in first and we move on.
                yield (k, b[k])
                # Alternatively, replace this with exception raiser to alert you of value conflicts
        elif k in a:
            yield (k, a[k])
        else:
            yield (k, b[k])
