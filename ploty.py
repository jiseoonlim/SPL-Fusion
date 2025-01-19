import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import time

# Figure 생성
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# 초기 데이터
x, y, z = [], [], []

# 그래프 업데이트 함수
def update_graph(new_x, new_y, new_z):
    x.append(new_x)
    y.append(new_y)
    z.append(new_z)

    ax.clear()  # 기존 그래프 삭제
    ax.scatter(x, y, z, c='blue', marker='o')
    plt.draw()
    plt.pause(0.1)

# 실시간 데이터 업데이트
for i in range(100):
    new_x = np.random.rand(1)[0]
    new_y = np.random.rand(1)[0]
    new_z = np.random.rand(1)[0]

    update_graph(new_x, new_y, new_z)
    time.sleep(0.1)  # 업데이트 주기
