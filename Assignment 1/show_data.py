import pandas as pd
import matplotlib.pyplot as plt
import time
import numpy as np
import csv

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['font.family']='sans-serif'
#解决负号'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False
	
def main( ):
     data = pd.read_csv("compare.csv")
     pred = []
     real = []
     cnt = 0
     for num in data['predition']:
        if cnt>=100: break
        pred.append(num)
        cnt += 1

     cnt = 0
     for num in data['real']:
        if cnt>=100: break
        real.append(num)
        cnt += 1

     index = [i for i in range(1,101)]

     plt.plot(index, pred, color='red', marker = 'o', label = 'pred')
     plt.plot(index, real, color = 'black', marker = '2', label = 'real')

     plt.title('预测与实际比较')

     plt.xlabel('样本序号')
     plt.ylabel('评分')

     plt.legend()
     plt.show()
	
if __name__ == "__main__":
	main()
