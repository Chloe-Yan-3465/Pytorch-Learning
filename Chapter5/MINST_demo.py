import torch
import torch.nn as nn
import numpy as np
import einops.layers.torch as elt

#载入数据
x_train = np.load("../dataset/mnist/x_train.npy")
y_train_label = np.load("../dataset/mnist/y_train_label.npy")

x_train = np.expand_dims(x_train,axis=1)
print(x_train.shape)

'''
Depthwise Convolution
'''
depth_conv = nn.Conv2d(
    in_channels=12,         # 输入通道数 12
    out_channels=12,        # 输出通道数 12（注意：每组输出 2 通道，见 groups=6）
    kernel_size=3,          # 卷积核大小 3x3
    groups=6,               # 分组卷积，将 12 个输入通道分为 6 组（每组 2 个输入 -> 2 个输出）
    dilation=2              # 膨胀因子为 2，增大感受野
)


'''
Pointwise Convolution
'''
point_conv = nn.Conv2d(
    in_channels=12,         # 输入来自上面的 depth_conv 的输出
    out_channels=24,        # 输出通道数提升为 24
    kernel_size=1           # 使用 1x1 卷积融合各通道
)


'''
将二者组合成一个模块，先做 depth/group-wise 卷积，再做 pointwise 卷积，这就是：

深度可分离卷积 Depthwise Separable Convolution + 膨胀卷积 Dilation

深度，可分离，膨胀 卷积定义
'''
depthwise_separable_conv = torch.nn.Sequential(depth_conv, point_conv)



class MnistNetword(nn.Module):
    def __init__(self):
        super(MnistNetword, self).__init__()
        self.convs_stack = nn.Sequential(
            nn.Conv2d(1, 12, kernel_size=7),     # 输入通道1，输出通道12，7x7大卷积核
            nn.ReLU(),                           # 激活函数
            depthwise_separable_conv,           # 深度可分离卷积（你前面定义过的组合卷积）
            nn.ReLU(),                           # 再次激活
            nn.Conv2d(24, 6, kernel_size=3)      # 标准卷积：输入通道24，输出通道6
        )

        self.logits_layer = nn.Linear(in_features=1536,out_features=10) 
            # 输入特征数量1536（根据卷积层输出大小算出来的）；输出维度是10，对应MINST的10类（数字0-9）

    def forward(self, inputs):
        image = inputs
        x = self.convs_stack(image)                        # 卷积层堆栈
        x = elt.Rearrange("b c h w -> b (c h w)")(x)       # 展平：把 [batch, channel, height, width] 转成 [batch, feature]
        logits = self.logits_layer(x)                      # 全连接分类
        return logits



device = "cuda" if torch.cuda.is_available() else "cpu"
#注意记得需要将model发送到GPU计算
model = MnistNetword().to(device)
#model = torch.compile(model)            #PyTorch 2.0的特性，加速计算速度，选择使用
loss_fn = nn.CrossEntropyLoss() # 交叉熵作为LOSS


'''
设置模型优化器
根据LOSS的梯度调整参数的工具
'''
optimizer = torch.optim.SGD(model.parameters(), lr=1e-4)



batch_size = 128    # batch=128，每次用128个样本做一次参数更新
for epoch in range(63):     # 训练63轮次
    train_num = len(x_train)//128
    train_loss = 0.
    for i in range(train_num):
        start = i * batch_size
        end = (i + 1) * batch_size

        x_batch = torch.tensor(x_train[start:end]).to(device) # device是CPU/GPU
        y_batch = torch.tensor(y_train_label[start:end]).to(device)

        pred = model(x_batch) # 向前传播，预测输出
        loss = loss_fn(pred, y_batch) # 计算损失

        optimizer.zero_grad()  # 梯度清零（防止累积）
        loss.backward()        # 反向传播：自动求梯度
        optimizer.step()       # 参数更新：执行一步梯度下降


        train_loss += loss.item()  # 记录每个批次的损失值

    # 计算并打印损失值
    train_loss /= train_num
    accuracy = (pred.argmax(1) == y_batch).type(torch.float32).sum().item() / batch_size
    print("epoch：",epoch,"train_loss:", round(train_loss,2),"accuracy:",round(accuracy,2))
