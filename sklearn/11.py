"""
Created on 2025/9/5 09:05 
Author: Shuijing
Description: 使用sklearn实现的0-9数字识别程序
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets, metrics
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

class DigitRecognizer:
    def __init__(self):
        # 加载sklearn内置的手写数字数据集
        self.digits = datasets.load_digits()
        self.model = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
    def prepare_data(self, test_size=0.3, random_state=42):
        """准备训练和测试数据"""
        # 数据集包含1797个样本，每个样本是一个8x8的图像，代表0-9的数字
        X = self.digits.data  # 特征数据，每个样本是64维向量(8x8)
        y = self.digits.target  # 标签，0-9的数字
        
        # 数据集分割为训练集和测试集
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        print(f"数据集加载完成：")
        print(f"- 总样本数：{X.shape[0]}")
        print(f"- 训练集样本数：{self.X_train.shape[0]}")
        print(f"- 测试集样本数：{self.X_test.shape[0]}")
        print(f"- 特征维度：{X.shape[1]} (8x8图像)")
        
        return self.X_train, self.X_test, self.y_train, self.y_test
        
    def train_model(self, model_type='knn', **kwargs):
        """训练模型，支持多种分类器"""
        if self.X_train is None:
            self.prepare_data()
            
        # 根据指定的模型类型选择分类器
        if model_type == 'knn':
            # K最近邻分类器
            n_neighbors = kwargs.get('n_neighbors', 5)
            self.model = KNeighborsClassifier(n_neighbors=n_neighbors)
        elif model_type == 'svm':
            # 支持向量机分类器
            kernel = kwargs.get('kernel', 'rbf')
            self.model = SVC(kernel=kernel, probability=True)
        elif model_type == 'random_forest':
            # 随机森林分类器
            n_estimators = kwargs.get('n_estimators', 100)
            self.model = RandomForestClassifier(n_estimators=n_estimators)
        else:
            raise ValueError("不支持的模型类型，请选择'knn'、'svm'或'random_forest'")
            
        # 训练模型
        print(f"开始训练{model_type.upper()}模型...")
        self.model.fit(self.X_train, self.y_train)
        print(f"模型训练完成")
        
        return self.model
        
    def evaluate_model(self):
        """评估模型性能"""
        if self.model is None:
            raise ValueError("请先训练模型")
            
        # 在测试集上进行预测
        y_pred = self.model.predict(self.X_test)
        
        # 计算准确率
        accuracy = metrics.accuracy_score(self.y_test, y_pred)
        print(f"模型准确率: {accuracy:.4f}")
        
        # 生成详细的分类报告
        print("\n分类报告:")
        print(classification_report(self.y_test, y_pred))
        
        # 生成混淆矩阵
        cm = confusion_matrix(self.y_test, y_pred)
        
        # 可视化混淆矩阵
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=range(10), yticklabels=range(10))
        plt.xlabel('预测标签')
        plt.ylabel('真实标签')
        plt.title('混淆矩阵')
        plt.show()
        
        return accuracy
        
    def predict_digit(self, image_data):
        """预测单个数字图像"""
        if self.model is None:
            raise ValueError("请先训练模型")
            
        # 确保输入数据形状正确
        if len(image_data.shape) == 2 and image_data.shape == (8, 8):
            # 如果输入是8x8的图像，将其展平为64维向量
            image_data = image_data.flatten().reshape(1, -1)
        elif len(image_data.shape) == 1 and image_data.shape[0] == 64:
            # 如果输入已经是64维向量，确保形状正确
            image_data = image_data.reshape(1, -1)
        else:
            raise ValueError("输入数据格式不正确，请提供8x8的图像或64维向量")
            
        # 进行预测
        prediction = self.model.predict(image_data)
        # 获取预测概率
        probabilities = self.model.predict_proba(image_data)[0]
        
        return {
            'predicted_digit': int(prediction[0]),
            'confidence': float(max(probabilities)),
            'all_probabilities': {i: float(prob) for i, prob in enumerate(probabilities)}
        }
        
    def visualize_samples(self, num_samples=10):
        """可视化数据集中的样本"""
        fig, axes = plt.subplots(1, min(num_samples, 10), figsize=(12, 3))
        
        for i, ax in enumerate(axes):
            ax.imshow(self.digits.images[i], cmap=plt.cm.gray_r, interpolation='nearest')
            ax.set_title(f"标签: {self.digits.target[i]}")
            ax.axis('off')
            
        plt.tight_layout()
        plt.show()

    def run_full_pipeline(self, model_type='knn', **kwargs):
        """运行完整的数字识别流程"""
        print(f"===== 数字识别程序 =====")
        
        # 1. 准备数据
        self.prepare_data()
        
        # 2. 可视化样本
        print("\n可视化数据集中的样本...")
        self.visualize_samples()
        
        # 3. 训练模型
        self.train_model(model_type=model_type, **kwargs)
        
        # 4. 评估模型
        print("\n评估模型性能...")
        accuracy = self.evaluate_model()
        
        print(f"\n数字识别流程完成，最终准确率: {accuracy:.4f}")

if __name__ == '__main__':
    # 创建数字识别器实例
    digit_recognizer = DigitRecognizer()
    
    # 运行完整的数字识别流程
    # 可以选择不同的模型：'knn', 'svm', 'random_forest'
    digit_recognizer.run_full_pipeline(model_type='knn')
    
    # 示例：使用其他模型
    # digit_recognizer.run_full_pipeline(model_type='svm', kernel='linear')
    # digit_recognizer.run_full_pipeline(model_type='random_forest', n_estimators=200)
    
    # 示例：使用训练好的模型进行预测
    if digit_recognizer.model is not None:
        # 从测试集中选一个样本进行预测
        sample_index = 0
        sample_image = digit_recognizer.digits.images[sample_index]
        
        print(f"\n预测样本图像（真实标签: {digit_recognizer.digits.target[sample_index]}）...")
        result = digit_recognizer.predict_digit(sample_image)
        
        print(f"预测结果: {result['predicted_digit']}")
        print(f"置信度: {result['confidence']:.4f}")
        print("各类别概率:")
        for digit, prob in result['all_probabilities'].items():
            if prob > 0.01:  # 只显示概率大于1%的类别
                print(f"  数字{digit}: {prob:.4f}")