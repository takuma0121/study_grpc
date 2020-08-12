import grpc
import time
import simple_pb2
import simple_pb2_grpc
from concurrent import futures
import pings
import datetime

# protoファイルのService + Servicer


class SimpleServiceServicer(simple_pb2_grpc.SimpleServiceServicer):
    def __init__(self):
        pass

    # protoファイルのrpcと合わせる
    def SimpleSend(self, request, context):
        print('logging: name {}, msg {}'.format(request.name, request.msg))
        # protoファイルのResponseと一致させる
        return simple_pb2.SimpleResponse(reply_msg='Hello! ' + request.name + '. Your message is ' + request.msg)


class ServerStreamingServiceServicer(simple_pb2_grpc.ServerStreamingServiceServicer):
    def __init__(self):
        pass

    def ServerStreamingSend(self, request, context):
        p = pings.Ping()
        print('logging: dest {}, count {}'.format(
            request.destination, request.count))
        # protoファイルのResponseと一致させる
        while True:
            value = p.ping(request.destination)
            time = str(datetime.datetime.today().time().strftime("%H:%M:%S"))
            yield simple_pb2.SimpleResponse(avg_rtt=value.avg_rtt, time=time)


# start server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
# simple_pb2_grpc.add_SimpleServiceServicer_to_server(SimpleServiceServicer(), server)
simple_pb2_grpc.add_ServerStreamingServiceServicer_to_server(
    ServerStreamingServiceServicer(), server
)
server.add_insecure_port('[::]:5051')
server.start()
print('run server')

# wait
try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    # stop server
    server.stop(0)
