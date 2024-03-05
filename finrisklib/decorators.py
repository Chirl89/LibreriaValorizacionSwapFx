import tracemalloc
from time import perf_counter


def measure_performance():
    """Medir performance

    Mide la performance de una función

    :return: Performance de la función
    """

    def wrapper(func):

        def wrapped(*args, **kwargs):

            tracemalloc.start()
            start_time = perf_counter()
            results = func(*args, **kwargs)
            current, peak = tracemalloc.get_traced_memory()
            finish_time = perf_counter()

            print(f'Function: {func.__name__}')
            print(f'Memory usage:\t\t {current / 10**6:.6f} MB \n'
                  f'Peak memory usage:\t {peak / 10**6:.6f} MB ')
            print(f'Time elapsed: {finish_time - start_time:.6f} seconds')
            print(f'{"-"*40}')
            tracemalloc.stop()
            return results

        return wrapped

    return wrapper
