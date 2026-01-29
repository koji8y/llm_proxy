from typing import Callable
import inspect

def show_result(func, to_show: Callable[[], bool] | None = None, **info):
    async def wrapper_async(*args, **kwargs):
        if to_show is not None and to_show():
            from icecream import ic
        try:
            result = '(unassigned due to exception)'
            result = await func(*args, **kwargs)
        except Exception:
            if to_show is not None and to_show():
                if info:
                    ic('raising exception', func.__name__, info, type(result), result)
                else:
                    ic('raising exception', func.__name__, type(result), result)
                raise
        if to_show is not None and to_show():
            if info:
                ic(func.__name__, info, type(result), result)
            else:
                ic(func.__name__, type(result), result)
        return result

    def wrapper_sync(*args, **kwargs):
        if to_show is not None and to_show():
            from icecream import ic
        try:
            result = '(unassigned due to exception)'
            result = func(*args, **kwargs)
        except Exception:
            if to_show is not None and to_show():
                if info:
                    ic('raising exception', func.__name__, info, type(result), result)
                else:
                    ic('raising exception', func.__name__, type(result), result)
                raise
        if to_show is not None and to_show():
            if info:
                ic(func.__name__, info, type(result), result)
            else:
                ic(func.__name__, type(result), result)
        return result

    wrapper = wrapper_async if inspect.iscoroutinefunction(func) else wrapper_sync
    wrapper.__annotations__ = func.__annotations__
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__signature__ = inspect.signature(func)
    return wrapper


def show_result_with_control(enable: bool = True, to_show: Callable[[], bool] | None = None, **info):
    if not enable:
        def decorator(func):
            return func
        return decorator

    def decorator(func):
        return show_result(func, to_show=to_show, **info)
    return decorator
