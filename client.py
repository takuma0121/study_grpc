import grpc
import simple_pb2
import simple_pb2_grpc
import argparse
import matplotlib
import matplotlib.pyplot as plt
import japanize_matplotlib


# 引数
parser = argparse.ArgumentParser(description='Ping結果を可視化するツール')
parser.add_argument('--destination', type=str,
                    default='google.com', help='pingの宛先')
parser.add_argument('--top', type=int, default=1, help='pingの回数')
parser.add_argument('--tmax', type=int, default=20, help='表示時間[s]')
parser.add_argument('--dmax', type=int, default=200, help='表示最大遅延時間[ms]')
args = parser.parse_args()

# グラフの概要を作成
fig = plt.figure()
fig.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.95)
# 初期グラフ作成
ax = fig.add_subplot(1, 1, 1, xlabel="time", ylabel="network delay[ms]")
ax.set_title(args.destination)
ax.set_xticks([])
ax.set_ylim(0, args.dmax)
x = [str(0) for i in range(0, args.tmax)]
y = [0 for i in range(0, args.tmax)]
line, = ax.plot(x, y, marker='o')

try:
    with grpc.insecure_channel('localhost:5051') as channel:
        stub = simple_pb2_grpc.ServerStreamingServiceStub(channel)
        destination = args.destination
        count = args.top
        responses = stub.ServerStreamingSend(
            simple_pb2.SimpleRequest(destination=destination, count=count)
        )

        for r in responses:
            print('RTT: {}, TIME: {}'.format(r.avg_rtt, r.time))
            del x[0]
            x.append(r.time)
            del y[0]
            y.append(r.avg_rtt)
            # 描画
            line.set_data(x, y)
            ax.set_xlim(min(x), max(x))
            plt.pause(.05)

except KeyboardInterrupt:
    exit(0)
