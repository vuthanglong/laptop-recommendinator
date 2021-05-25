import torch
import torch.nn as nn
import torch.nn.functional as F
from .attention import Attention

class BiLSTM(nn.Module):
    
    def __init__(self,input_size1,hidden_size1,output_size,embedd_matrix,bidirectional = True, num_layer = 1):
        super(BiLSTM, self).__init__()
        if bidirectional == True:
          bi = 2
        else: bi = 1
        MAX_FEATURE = 2000
        embed_size = 120
        max_len = 25
        self.hidden_size1 = hidden_size1
        self.input_size1 = input_size1
        self.n_classes = output_size
        self.batch_size = 128
        self.attention = Attention(self.hidden_size1 *bi, max_len)
        self.embedding = nn.Embedding(MAX_FEATURE, embed_size)
        self.embedding.weight = nn.Parameter(torch.tensor(embedd_matrix, dtype=torch.float32))
        self.embedding.weight.requires_grad = False
        self.lstm = nn.LSTM(embed_size, self.hidden_size1, bidirectional=bidirectional, batch_first=True)
        self.linear = nn.Linear(self.hidden_size1 * bi, 256)
        self.batchnorm1d1 = nn.BatchNorm1d(self.hidden_size1*bi)
        self.batchnorm1d2 = nn.BatchNorm1d(256)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.out = nn.Linear(256, self.n_classes)


    def forward(self, x):
        h_embedding = self.embedding(x.long())
        h_lstm, _= self.lstm(h_embedding)
        out1 = self.attention(h_lstm)
        out1 = self.dropout(out1)
        out1 = self.relu(self.batchnorm1d1(out1))
        out1 = self.linear(out1)
        out1 = self.batchnorm1d2(out1)
        out1 = self.relu(out1)
        out1 = self.out(out1)
        return out1
      
    def predict_model(self, input, pro=False):
        self.eval()
        output = self(input)
        if pro is True:
            #sm = nn.Softmax()
            torch.set_printoptions(sci_mode=False)
            prob = F.softmax(output)
            top2_prob, top2_label = torch.topk(prob, 2)
            top2_prob = top2_prob.detach().numpy()
            top2_label = top2_label.detach().numpy()
            return top2_prob, top2_label
        else:
            preds = torch.nn.functional.log_softmax(output.detach(), -1).cpu().numpy().argmax(axis=1)
            return preds