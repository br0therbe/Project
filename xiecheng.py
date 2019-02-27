from gevent import monkey; monkey.patch_all()
from gevent.queue import Queue
from jddetailpage import JDDetailPage
from time import time
import gevent
import json


class XieCheng(object):
    def __init__(self, urls, func):
        self.urls = urls
        self.func = func
        self.queue = self.list_to_queue()
        self.value = list()

    def list_to_queue(self):
        queue = Queue()
        for each in self.urls:
            queue.put_nowait(each)
        return queue

    def parse(self, queue):
        while not queue.empty():
            url = queue.get_nowait()
            print(url, gevent.getcurrent())
            try:
                self.value.append(self.func(url))
            except Exception as e:
                print(''.join(['url:', str(url), '获取失败']), e)
                continue
            gevent.sleep(0)

    def work(self, num=4):
        gevent.joinall([gevent.spawn(self.parse, self.queue) for i in range(num)])


if __name__ == '__main__':
    li = ['8674557', '8461498', '100000612187', '100000769432', '100000769466', '100000679465', '8461496', '8461490', '100000667974', '100001234930', '100001234898', '8461500', '100000430140', '8736570', '100001895678']
    # li = ['8674557', '8461498', '100000612187']
    start_time = time()
    jddp = JDDetailPage()
    xc = XieCheng(li, jddp.parse)
    xc.work()
    end_time = time()
    print("spend time:  {}s".format(end_time - start_time))
    start_time = time()
    # with open(r'C:\Users\11021\Desktop\detail.txt', 'w') as fp:
    #         fp.write(json.dumps([list(i) for i in xc.value], ensure_ascii=False))
    # end_time = time()
    with open(r'C:\Users\11021\Desktop\detail.txt', 'w') as fp:
            fp.write(str([list(i) for i in xc.value]))
    end_time = time()
    print("spend time:  {}s".format(end_time - start_time))
    pass


