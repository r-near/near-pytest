import near  # type: ignore
import json


# Store the count in contract storage
@near.export
def new():
    """Initialize the contract with a starting count."""
    args = json.loads(near.input())
    starting_count = args.get("starting_count", 0)
    near.storage_write("count", str(starting_count))
    near.value_return("true")
    return True


@near.export
def increment():
    """Increment the counter and return the new value."""
    count = int(near.storage_read("count") or 0)
    count += 1
    near.storage_write("count", str(count))
    near.value_return(str(count))
    return count


@near.export
def decrement():
    """Decrement the counter and return the new value."""
    count = int(near.storage_read("count") or 0)
    count -= 1
    near.storage_write("count", str(count))
    near.value_return(str(count))
    return count


@near.export
def get_count():
    """Get the current count."""
    count = int(near.storage_read("count") or 0)
    near.value_return(str(count))
    return count


@near.export
def reset():
    """Reset the counter to the given value."""
    args = json.loads(near.input())
    value = args.get("value", 0)
    near.storage_write("count", str(value))
    near.value_return(str(value))
    return value
