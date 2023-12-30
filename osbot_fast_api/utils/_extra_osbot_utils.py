import uuid


def list_minus_list(list_a, list_b):
    return [item for item in list_a if item not in list_b]

def is_guid(value):
    try:
        uuid.UUID(value, version=4)
        return True
    except ValueError:
        return False