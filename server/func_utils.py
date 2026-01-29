import inspect

def show_result(func):
    async def wrapper_async(*args, **kwargs):
        try:
            result = '(unassigned due to exception)'
            result = await func(*args, **kwargs)
        except Exception:
            from icecream import ic; ic('raising exception', func.__name__, type(result), result)
            raise
        from icecream import ic; ic(func.__name__, type(result), result)
        return result

    def wrapper_sync(*args, **kwargs):
        try:
            result = '(unassigned due to exception)'
            result = func(*args, **kwargs)
        except Exception:
            from icecream import ic; ic('raising exception', func.__name__, type(result), result)
            raise
        from icecream import ic; ic(func.__name__, type(result), result)
        return result

    wrapper = wrapper_async if inspect.iscoroutinefunction(func) else wrapper_sync
    wrapper.__annotations__ = func.__annotations__
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__signature__ = inspect.signature(func)
    return wrapper
