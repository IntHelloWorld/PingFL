import os
import time
from multiprocessing import Pool, TimeoutError


def f(x):
    time.sleep(x)
    print("waited for", x, "seconds")
    if x == 3:
        raise Exception("x == 3")


if __name__ == "__main__":
    # 启动 4 个工作进程
    with Pool(processes=4) as pool:

        # 异步地进行多次求值 *可能* 会使用更多进程
        async_results = []
        for i in [7, 5, 3, 9]:
            async_results.append(pool.apply_async(f, (i,)))

        results = []
        for i in async_results:
            try:
                results.append(i.get())
            except Exception as e:
                print("Caught exception: ", e)

    print("Results: ", results)
