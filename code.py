from typing import Tuple


import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
import torch.nn.functional as F


class MLP(nn.Module):
    """
    根据论文 The MLP has a hidden layer with tanh activation and softmax output layer in our experiments.
    这里损失函数写到 model 里面去
    """
    def __init__(self, in_features: int, hidden_features: int, class_num: int):
        """
        :param in_features: 输入的数据维数
        :param hidden_features: 隐藏层的维数
        :param class_num: 分类数目
        """
        super().__init__()
        self.full_conn1 = nn.Linear(in_features, hidden_features)
        self.tanh = nn.Tanh()
        self.full_conn2 = nn.Linear(hidden_features, class_num)
        self.loss_func = nn.CrossEntropyLoss()

    def get_scores(self, x: torch.Tensor) -> torch.Tensor:
        """
        获取分数，为了准确率验证
        :param x: shape: (batch_size, in_features)
        :return: scores shape: (batch_size, class_num)
        """
        return self.full_conn2(self.tanh(self.full_conn1(x)))


class BiLSTM(nn.Module):
    def __init__(self, input_size: int, hidden_size: int):
        """

        :param input_size: 输入维度
        :param hidden_size: h 维数；注意由于 bidirectional 的存在，我们会有 x2 或 /2 操作
        """
        super().__init__()
        self.bi_lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, bidirectional=True, batch_first=True)

    def forward(self, tensor_sentences: torch.Tensor, seq_lengths: torch.Tensor) -> torch.Tensor:
        """
        :param tensor_sentences: (batch_size, max_sentence_length, input_size)
        :param seq_lengths: shape: (batch_size,) ；每句话的实际长度
        :return: shape: (batch_size, max_sentence_length, 2 * hidden_size)  hidden_size 是说 BiLSTM 初始化输入 hidden_size
        """
        packed_sentences = pack_padded_sequence(tensor_sentences, seq_lengths, batch_first=True, enforce_sorted=False)  # 函数内自动进行排序
        output, _ = self.bi_lstm(packed_sentences)
        result, _ = pad_packed_sequence(output, batch_first=True)
        return result
