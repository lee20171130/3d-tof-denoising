#!/usr/bin/env python

import torch
import torch.nn as nn

"""
Idea is to use two different models, the first model predicting the lighting and other parameters from the input image; and the second model predicting True Depth Map using parameters from first model along with False Depth Map.

Model A
=======

Input  : False Depth Map
Output : Light Position, Camera Position, Material Properties

Model B
=======

Input  : False Depth Map, Output of Model A
Output : True Depth Map 

"""

class Model_A(nn.Module):
    def __init__(self, config):
        super(Model_A, self).__init__()
        self.config = config
        self.layer1 = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=16, kernel_size=5, stride=1, padding=2),
            nn.ReLU(),
            nn.BatchNorm2d(16),            
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer2 = nn.Sequential(
            nn.Conv2d(in_channels=16, out_channels=32, kernel_size=5, stride=1, padding=2),
            nn.ReLU(),
            nn.BatchNorm2d(32),            
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer3 = nn.Sequential(
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=5, stride=1, padding=2),
            nn.ReLU(),
            nn.BatchNorm2d(64),            
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer4 = nn.Sequential(
            nn.Conv2d(in_channels=64, out_channels=32, kernel_size=5, stride=1, padding=2),
            nn.ReLU(),
            nn.BatchNorm2d(32),            
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer5 = nn.Sequential(
            nn.Conv2d(in_channels=32, out_channels=16, kernel_size=5, stride=1, padding=2),
            nn.ReLU(),
            nn.BatchNorm2d(16),            
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.fc = nn.Linear(in_features=13*16*16, out_features=self.config.data.parameters)

    def forward(self, x):
        out = self.layer1(x)
        # print("Layer 1 Output Shape : {}".format(out.shape))
        out = self.layer2(out)
        # print("Layer 2 Output Shape : {}".format(out.shape))
        out = self.layer3(out)
        # print("Layer 3 Output Shape : {}".format(out.shape))
        out = self.layer4(out)
        # print("Layer 4 Output Shape : {}".format(out.shape))
        out = self.layer5(out)
        # print("Layer 5 Output Shape : {}".format(out.shape))
        out = out.reshape(out.size(0), -1)
        # print("Layer reshape Output Shape : {}".format(out.shape))
        out = self.fc(out)
        # print("Layer FC Output Shape : {}".format(out.shape))
        return out

class Model_B(nn.Module):
    def __init__(self, config):
        super(Model_B, self).__init__()
        self.config = config
        # CNN layers for fdm
        self.layer1 = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=16, kernel_size=5, stride=2, padding=2),
            nn.ReLU(),
            nn.BatchNorm2d(16))
        self.layer2 = nn.Sequential(
            nn.Conv2d(in_channels=16, out_channels=32, kernel_size=5, stride=2, padding=2),
            nn.ReLU(),
            nn.BatchNorm2d(32))
        self.layer3 = nn.Sequential(
            nn.Conv2d(in_channels=32, out_channels=32, kernel_size=5, stride=2, padding=2),
            nn.ReLU(),
            nn.BatchNorm2d(32))
        self.layer4 = nn.Sequential(
            # nn.ConvTranspose2d(in_channels=42, out_channels=32, kernel_size=5, stride=2, padding=2, output_padding=1),
            nn.ConvTranspose2d(in_channels=32, out_channels=32, kernel_size=5, stride=2, padding=2, output_padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(32))
        self.layer5 = nn.Sequential(
            nn.ConvTranspose2d(in_channels=32, out_channels=16, kernel_size=5, stride=2, padding=2,output_padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(16))
        self.layer6 = nn.Sequential(
            nn.ConvTranspose2d(in_channels=16, out_channels=1, kernel_size=5, stride=2, padding=2, output_padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(1))
        # CNN layer for parameters
        self.param_fc = nn.Sequential(
            nn.Linear(in_features=18, out_features=30),
            nn.ReLU(),
            nn.Linear(in_features=30, out_features=10)
            )

    def forward(self, x, y):
        out = self.layer1(x)
        # print('Shape of parameters : {}'.format(y.shape))
        out_param = self.param_fc(y)
        # print("LayerParam 1 Output Shape : {}".format(out_param.shape))
        # print("Layer 1 Output Shape : {}".format(out.shape))
        out = self.layer2(out)
        # print("Layer 2 Output Shape : {}".format(out.shape))
        out = self.layer3(out)
        N, C, H, W = out.shape
        out_param = out_param.unsqueeze(-1).unsqueeze(-1).expand(N, -1, H, W)
        out = torch.cat((out, out_param), dim=1)
        print("Layer 3 Output Shape : {}".format(out.shape))
        out = self.layer4(out)
        # print("Layer 4 Output Shape : {}".format(out.shape))
        out = self.layer5(out)
        # print("Layer 5 Output Shape : {}".format(out.shape))
        out = self.layer6(out)
        # print("Layer 6 Output Shape : {}".format(out.shape))
        return out