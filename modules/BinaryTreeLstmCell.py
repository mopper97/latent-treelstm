# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# import torch
# from torch import nn


# class BinaryTreeLstmCell(nn.Module):
#     def __init__(self, hidden_dim, dropout_prob=None):
#         super().__init__()
#         self.h_dim = hidden_dim
#         self.linear = nn.Linear(in_features=2 * self.h_dim, out_features=5 * self.h_dim)
#         if dropout_prob is not None:
#             self.dropout = nn.Dropout(dropout_prob)
#         self.reset_parameters()

#     def reset_parameters(self):
#         nn.init.orthogonal_(self.linear.weight)
#         # add some positive bias for the forget gates [b_g, b_i, b_f, b_f, b_o] = [0, 0, 1, 1, 0]
#         nn.init.constant_(self.linear.bias, val=0)
#         nn.init.constant_(self.linear.bias[2 * self.h_dim:4 * self.h_dim], val=1)

#     def forward(self, h_l, c_l, h_r, c_r):
#         h_lr = torch.cat([h_l, h_r], dim=-1)
#         g, i, f_l, f_r, o = self.linear(h_lr).chunk(chunks=5, dim=-1)
#         g, i, f_l, f_r, o = g.tanh_(), i.sigmoid_(), f_l.sigmoid_(), f_r.sigmoid_(), o.sigmoid_()
#         if hasattr(self, "dropout"):
#             c = i * self.dropout(g) + f_l * c_l + f_r * c_r
#         else:
#             c = i * g + f_l * c_l + f_r * c_r
#         h = o * c.tanh_()
#         return h, c


import torch
from torch import nn

class BinaryTreeLstmCell(nn.Module):
    def __init__(self, hidden_dim, dropout_prob=None):
        super().__init__()
        self.h_dim = hidden_dim
        self.linear = nn.Linear(in_features=2 * self.h_dim, out_features=5 * self.h_dim)
        if dropout_prob is not None:
            self.dropout = nn.Dropout(dropout_prob)
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.orthogonal_(self.linear.weight)
        # add some positive bias for the forget gates [b_g, b_i, b_f, b_f, b_o] = [0, 0, 1, 1, 0]
        nn.init.constant_(self.linear.bias, val=0)
        nn.init.constant_(self.linear.bias[2 * self.h_dim:4 * self.h_dim], val=1)

    def forward(self, h_l, c_l, h_r, c_r):
        h_lr = torch.cat([h_l, h_r], dim=-1)
        gates = self.linear(h_lr).chunk(chunks=5, dim=-1)
        
        # Replace in-place operations with out-of-place equivalents
        g = torch.tanh(gates[0])
        i = torch.sigmoid(gates[1])
        f_l = torch.sigmoid(gates[2])
        f_r = torch.sigmoid(gates[3])
        o = torch.sigmoid(gates[4])
        
        if hasattr(self, "dropout"):
            c = i * self.dropout(g) + f_l * c_l + f_r * c_r
        else:
            c = i * g + f_l * c_l + f_r * c_r
            
        # Replace in-place tanh with out-of-place version
        h = o * torch.tanh(c)
        
        return h, c