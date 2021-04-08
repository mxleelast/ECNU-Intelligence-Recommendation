import math
import csv

class ItemBasedCF:

    def __init__(self):
        """
        初始化对象
        """
        print("Program Launching!!!")
        print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")
        self.readData()
        print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")
        self.readTest()
        print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")

    def readData(self):
        """
        读取文件，并生成用户-物品
        用户-物品的评分表
        训练集
        """
        #将train.csv划分 80%为训练集，20%为测试集
        #train.csv文件一共大约有8000条数据字段，这里选取1600条为test集合
        self.rmse_user = [] 
        self.rmse_item = []
        self.rmse_star = []
        
        self.train = {}
        # 打开文件，读取训练集
        with open('train.csv','r') as csvfile:
          reader = csv.reader(csvfile)
          for i,rows in enumerate(reader):
               if i==0: continue
               row = rows
               user = row[0]
               item = row[1]
               star = row[3]
               self.train.setdefault(user,{})
               self.train[user][item] = star
               if(i<1600):
                    self.rmse_user.append(user)
                    self.rmse_item.append(item)
                    self.rmse_item.append(star)
        print("Train dataset loading OK!!!")
               
    def readTest(self):
        """
        读取测试文件
        """
        self.test_user = []
        self.test_item = []
        with open('test.csv','r+') as f:
            reader = csv.reader(f)
            for i,rows in enumerate(reader):
                if i==0: continue
                row = rows
                user = row[0]
                item = row[1]
                self.test_user.append(user)
                self.test_item.append(item)
        print("Test dataset loading OK!!!")

    def ItemSimilarity(self):
        """
        计算物品之间的相似度
        """
        C = {} #items-items矩阵 行为次数的矩阵   共现矩阵
        N = {} #记录items被多少个不同用户购买
        #遍历训练数据，获取用户对有过行为的物品
        for user, items in self.train.items():
            #遍历该用户每件物品项
            for i in items.keys():
                #该物品被用户评分则计数加1
                if i not in N.keys():
                    N.setdefault(i, 0)
                N[i] += 1

                # 物品-物品共现矩阵数据加1
                if i not in C.keys():
                    C.setdefault(i, {})
                for j in items.keys():
                    if i == j:
                        continue
                    if j not in C[i].keys():
                        C[i].setdefault(j, 0)
                    C[i][j] += 1
        #计算相似度矩阵，   计算物品-物品的相似度，余弦相似度
        self.W = {}
        for i, related_items in C.items():
            if i not in self.W.keys():
                self.W.setdefault(i, {})
            for j, cij in related_items.items():
                self.W[i][j] = cij / (math.sqrt(N[i] * N[j]))
        return self.W

    #给用户user推荐，前K个相关用户喜欢的
    def Recommend(self, user, K=5, N=10):
        """
        给用户推荐物品，取相似度最大的 K 个物品，推荐排名靠前的 N 个物品
        """
        '''
            :param user: 用户(str)
            :param K:  相似度的前K个          W[item].items()
            :param N:  最后算出来的结果的前N个
            :return:   返回最后的前N个值 rank
        '''
        # 用户对物品的偏好值
        rank = {}
        # 用户产生过行为的物品项和评分
        action_item = self.train[user]
        
        for item, score in action_item.items():
            #遍历与item最相似的前K个物品，获得这些物品及分数
            for j, wj in sorted(self.W[item].items(), key=lambda x: x[1], reverse=True)[0:K]:
                #若有该物品，跳过
                if j in action_item.keys():
                    continue
                if j not in rank.keys():
                    rank.setdefault(j, 0)
                rank[j] += int(float(score)) * wj
        return sorted(rank.items(), key=lambda x: x[1], reverse=True)[0:N]


if __name__ == "__main__":

    new_user = []
    new_item = []
    new_star = []

    cf = ItemBasedCF()
    cf.ItemSimilarity()

    print("Start to predict for test dataset!!!")
    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")
    L_user = cf.test_user  #获取test数据集的用户列表
    L_item = cf.test_item  #获取test数据集的商品列表
    
    #print(len(L_user),len(L_item))
    #首先对test中的每个用户都推荐 N=10 个物品 并给出相似分数
    #然后判断
    for k in range(len(L_user)):
        #print(k)
        ori_user = L_user[k]
        temp = cf.Recommend(ori_user)
        temp_item = []
        for t in temp:
            temp_item.append(t[0])
            
        item = L_item[k]
        if item in temp_item:
            score = 0.0
            num = 0
            for t in temp:
                score += t[1]
                num = num + 1
            score /= num
            #print(ori_user,item,int(score))
            new_user.append(ori_user)
            new_item.append(item)
            new_star.append(int(score))
            
        else:
            #如何设置初始评分 与相似度wj相乘？
            #一个想法是 计算当前物品产生所有评分的平均值 然后取整作为初始评分
            S = cf.train.items()
            score_final = 0.0
            counter = 0
            for user1,itemk in S:
                S_temp = itemk.keys()
                for i in S_temp:
                    if i==item:
                        score_final += float(itemk[i])
                        counter = counter + 1
            #设置当前初始评分，然后计算相似系数wj
            score = score_final / counter
            #print(score)
            #遍历与item最相似的1个物品，获得这个物品及分数
            for j, wj in sorted(cf.W[item].items(), key=lambda x: x[1], reverse=True)[0:1]:
                score = score * wj
            score_int = int(float(score))
            if score - score_int >= 0.5:
                score_int = score_int + 1
            score_int += 1
            if score_int >5: score_int = 5
            #print(ori_user,item,score_int)
            new_user.append(ori_user)
            new_item.append(item)
            new_star.append(score_int)

    print("Writing data to new file!!!")
    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")
    
    path = 'prediction.csv'
    with open(path, 'w', newline='') as f:
        file = csv.writer(f)
        file.writerow(['user_id','business_id','star'])
        for i in range(len(new_user)):
            file.writerow([new_user[i],new_item[i],new_star[i]])
        f.close()
    print("All Works Done!!!")
