from typing import Callable
import inspect

def show_result(func, to_show: Callable[[], bool] | None = None, exception_types_to_omit_traceback: tuple[type[Exception], ...] | None = None, **info):
    def default_func_to_show() -> bool:
        return False

    if to_show is None:
        to_show = default_func_to_show

    async def wrapper_async(*args, **kwargs):
        if to_show is not None and to_show():
            from icecream import ic
        try:
            # result = '(unassigned due to exception)'
            result = await func(*args, **kwargs)
        except Exception as exp:
            # if to_show is not None and to_show():
            #     if info:
            #         ic('raising exception', func.__name__, info, type(result), result)
            #     else:
            #         ic('raising exception', func.__name__, type(result), result)
            #     raise
            # from icecream import ic; ic(func.__name__, 'caught exception', exp)
            # from traceback import print_exc; print_exc()
            if to_show() and (exception_types_to_omit_traceback is None or not isinstance(exp, exception_types_to_omit_traceback)):
                if info:
                    ic('raising exception', func.__name__, info, type(result), result)
                else:
                    ic('raising exception', func.__name__, type(result), result)
                from traceback import print_exc; print_exc()
            
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
            # result = '(unassigned due to exception)'
            result = func(*args, **kwargs)
        except Exception as exp:
            # if to_show is not None and to_show():
            #     if info:
            #         ic('raising exception', func.__name__, info, type(result), result)
            #     else:
            #         ic('raising exception', func.__name__, type(result), result)
            #     raise
            # from icecream import ic; ic(func.__name__, 'caught exception', exp)
            # from traceback import print_exc; print_exc()
            if to_show() and (exception_types_to_omit_traceback is None or not isinstance(exp, exception_types_to_omit_traceback)):
                if info:
                    ic('raising exception', func.__name__, info, type(result), result)
                else:
                    ic('raising exception', func.__name__, type(result), result)
                from traceback import print_exc; print_exc()
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


def show_result_with_control(enable: bool = True, to_show: Callable[[], bool] | None = None, exception_types_to_omit_traceback: tuple[type[Exception], ...] | None = None, **info):
    if not enable:
        def decorator(func):
            return func
        return decorator

    def decorator(func):
        return show_result(func, to_show=to_show, exception_types_to_omit_traceback=exception_types_to_omit_traceback, **info)
    return decorator
