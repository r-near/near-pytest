# examples/counter_contract/__init__.py
import near


# Store the count in contract storage
@near.export
def new(starting_count=0):
    """Initialize the contract with a starting count."""
    near.storage_write("count", starting_count)
    return True


@near.export
def increment():
    """Increment the counter and return the new value."""
    count = near.storage_read("count") or 0
    count += 1
    near.storage_write("count", count)
    return count


@near.export
def decrement():
    """Decrement the counter and return the new value."""
    count = near.storage_read("count") or 0
    count -= 1
    near.storage_write("count", count)
    return count


@near.export
def get_count():
    """Get the current count."""
    return near.storage_read("count") or 0


@near.export
def reset(value=0):
    """Reset the counter to the given value."""
    near.storage_write("count", value)
    return value
