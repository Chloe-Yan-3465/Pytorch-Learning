# 链式法则与一元线性回归

## y=wx+b，求w和b

### step1.梯度下降法（Gradient Descent）

在一元线性回归中，我们希望找到参数 $w$ 和 $b$，使得预测值：

$\hat{y}_i = wx_i + b$

能够尽可能接近真实值 $y_i$。我们使用均方误差（MSE）作为损失函数：

$L(w, b) = \frac{1}{n} \sum_{i=1}^n (wx_i + b - y_i)^2$

### step2.对参数求导（使用链式法则）

我们对损失函数分别对 $w$ 和 $b$ 求偏导数：

- 对 $w$ 的偏导：

$\frac{\partial L}{\partial w} = \frac{2}{n} \sum_{i=1}^n (wx_i + b - y_i) \cdot x_i$

- 对 $b$ 的偏导：

$\frac{\partial L}{\partial b} = \frac{2}{n} \sum_{i=1}^n (wx_i + b - y_i)$

这些推导中，对复合函数 $(wx_i + b - y_i)^2$ 求导，应用了**链式法则（Chain Rule）**：先对外层平方函数求导（导数是 $2z$），再乘上内层对参数的导数（$x_i$ 或常数 1）。

### step3.更新公式（梯度下降）

使用学习率 $\alpha$ 来更新参数：

$w \leftarrow w - \alpha \cdot \frac{\partial L}{\partial w}$

$b \leftarrow b - \alpha \cdot \frac{\partial L}{\partial b}$  

不断重复以上步骤，直到损失函数收敛或达到预设迭代次数。


## 对比最小二乘法和梯度下降算法：
最小二乘是导数为0，然后解得w、b；  
梯度下降是从随机点出发，试探性，能解决 解不出导数为0点的问题
