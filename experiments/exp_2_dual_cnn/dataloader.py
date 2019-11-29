#!/usr/bin/env python

import os
from os import listdir
from os.path import isfile, join
import glob
import pickle
import imageio
import torch
import pandas as pd
import h5py
import cv2
from skimage import io, transform
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils

# Ignore warnings
import warnings
warnings.filterwarnings("ignore")

plt.ion()   # interactive mode

static = "/storage-pod/3d-tof-denoising/data/FLAT/FLAT/trans_render/static"
dynamic = "/storage-pod/3d-tof-denoising/data/FLAT/FLAT/trans_render/dyn"
full = "/storage-pod/3d-tof-denoising/data/FLAT/FLAT/kinect/full"
ref = "/storage-pod/3d-tof-denoising/data/FLAT/FLAT/kinect/reflection"
gt = "/storage-pod/3d-tof-denoising/data/FLAT/FLAT/kinect/gt" 

# static = "C:/Users/kapil/Documents/3d-tof-denoising/data/FLAT/FLAT/trans_render/static"
# dynamic = "C:/Users/kapil/Documents/3d-tof-denoising/data/FLAT/FLAT/trans_render/dyn"
# full = "C:/Users/kapil/Documents/3d-tof-denoising/data/FLAT/FLAT/kinect/full"
# gt = "C:/Users/kapil/Documents/3d-tof-denoising/data/FLAT/FLAT/kinect/gt" 

static_data = []
dynamic_data = []

"""
os.chdir(static)
for f in glob.glob("*.pickle"):
	with open(f,'rb') as file:
		data = pickle.load(file)
		static_data.append(data)

os.chdir(dyn)
for f in glob.glob("*.pickle"):
	with open(f,'rb') as file:
		data = pickle.load(file)
		dynamic_data.append(data)
"""

full_files = [f for f in listdir(full) if isfile(join(full, f))]
gt_files   = [f for f in listdir(gt) if isfile(join(gt, f))]
ref_files  = [f for f in listdir(ref) if isfile(join(ref, f))]
image_files = list(set(ref_files) & set(gt_files))
print(len(image_files))

"""
def loadTrainingData_A(args):
	fdm = []
	parameters = []
	for i in image_files:
		try:
			with open(join(static, i + ".pickle"),'rb') as file:
				data = pickle.load(file)
				param = {}
				param['scene'] = data['scene']
				param['prop_idx'] = data['prop_idx']
				param['cam'] = data['cam']
				parameters.append(param)
			
				false_dm = np.fromfile(join(full, i), dtype=np.int32)
				false_dm = false_dm.reshape((424, 512, 9)).astype(np.float32)

		except:
			print('[!] File {} not found'.format(i))

	return (fdm, parameters)

def loadTestData_A(args):
	fdm = []
	parameters = []
	for i in image_files:
		try:
			with open(join(static, i + ".pickle"),'rb') as file:
				data = pickle.load(file)
				param = {}
				param['scene'] = data['scene']
				param['prop_idx'] = data['prop_idx']
				param['cam'] = data['cam']
				parameters.append(param)

			false_dm = np.fromfile(join(full, i), dtype=np.int32)
			false_dm = false_dm.reshape((424, 512, 9)).astype(np.float32)
	
		except:
			print('[!] File {} not found'.format(i))

	return (fdm, parameters)
"""
# param = {}
# keys = ['scene', 'prop_idx', 'cam']
# with open(join(static, "1569126364657171.pickle"), 'rb') as file:
# 	data = pickle.load(file)
# 	param = dict((k, data[k]) for k in keys if k in data)
# 	light = np.array(param['scene']['light'])
# 	light = np.where(light=='-point-light-source', 1, light)

params = np.load(join(static, 'data.npy'))
param_filenames = []
for i in params:
	param_filenames.append(os.path.splitext(i[0])[0])
# param = np.where(params[0]=='-point-light-source', 1, params[0])
# param = param[1:].astype(np.float64)

def loadTrainingData_A(args):
	fdm = []
	parameters = []
	for i in image_files:
		try:
			false_dm = np.fromfile(join(ref, i), dtype=np.int32)
			false_dm = Image.fromarray(false_dm.reshape((424, 512, 9)).astype(np.uint8)[:,:,1])
			fdm.append(false_dm)
			pos = np.where(param_filenames == i)
			param = params[pos[0][0], 1:]
			parameters.append(param)
		except:
			print('[!] File {} not found'.format(i))

	return (fdm, parameters)

def loadTestData_A(args):
	fdm = []
	parameters = []
	for i in image_files:
		try:
			false_dm = np.fromfile(join(ref, i), dtype=np.int32)
			false_dm = Image.fromarray(false_dm.reshape((424, 512, 9)).astype(np.uint8)[:,:,1])
			fdm.append(false_dm)
			parameters.append(light)
		except:
			print('[!] File {} not found'.format(i))

	return (fdm, parameters)

def loadTrainingData_B(args):
	fdm = []
	tdm = []
	parameters = []
	for data in static_data:
		fdm.append(data['depth_true'])
		tdm.append(data['depth_true'])
		param = {}
		param['scene'] = data['scene']
		param['prop_idx'] = data['prop_idx']
		param['cam'] = data['cam']
		parameters.append(param)
	return (fdm, parameters, tdm)


def loadTestData_B(args):
	fdm = []
	tdm = []
	parameters = []
	for data in dynamic_data:
		fdm.append(data['depth_true'])
		tdm.append(data['depth_true'])
		param = {}
		param['scene'] = data['scene']
		param['prop_idx'] = data['prop_idx']
		param['cam'] = data['cam']
		parameters.append(param)
	return (fdm, parameters, tdm)

def loadDeeptofTrainingData(args):
	depth_ref_images = []
	mpi_abs_images = []
	with h5py.File('DeepToF_training_6.7k_256x256.h5', 'r') as f:
		depth_ref = list(f['depth_ref'])
		mpi_abs = list(f['mpi_abs'])
	for i in range(len(depth_ref)):
		depth_ref_images.append(cv2.imresize(np.reshape(depth_ref[0], (256, 256)), (424, 512)))
		mpi_abs_images.append(cv2.imresize(np.reshape(mpi_abs[0], (256, 256)), (424, 512)))

	return (depth_ref_images, mpi_abs_images)

def loadDeeptofTestData(args):
	depth_ref_images = []
	mpi_abs_images = []
	with h5py.File('DeepToF_validation_1.7k_256x256.h5', 'r') as f:
		depth_ref = list(f['depth_ref'])
		mpi_abs = list(f['mpi_abs'])
	for i in range(len(depth_ref)):
		depth_ref_images.append(cv2.imresize(np.reshape(depth_ref[0], (256, 256)), (424, 512)))
		mpi_abs_images.append(cv2.imresize(np.reshape(mpi_abs[0], (256, 256)), (424, 512)))
	
	return (depth_ref_images, mpi_abs_images)

"""

Model A
=======

Input  : False Depth Map
Output : Parameter List (present in config file)

Model B
=======

Input  : Parameter List, False Depth Map
Output : True Depth Map

"""

class Flat_ModelA(Dataset):
	def __init__(self, args, train=True, transform=None):
		self.args = args
		if train == True:
			self.fdm, self.parameters = loadTrainingData_A(args)
		else:
			self.fdm, self.parameters = loadTestData_A(args)
		self.data_size = len(self.fdm)
		self.transform = transforms.Compose([transforms.ToTensor()])

	def __getitem__(self, index):
		return (self.transform(self.fdm[index]).double(), torch.from_numpy(self.parameters[index]).double())

	def __len__(self):
		return self.data_size

class Flat_ModelB(Dataset):
	def __init__(self, args, train=True, transform=None):
		self.args = args
		if train == True:
			self.fdm, self.parameters, self.tdm = loadTrainingData_B(self.args)
		else:
			self.fdm, self.parameters, self.tdm = loadTestData_B(self.args)
		self.data_size = len(self.parameters)
		self.transform = transform

	def __getitem__(self, index):
		return (self.fdm[index], self.parameters[index], self.tdm[index])

	def __len__(self):
		return self.data_size

class Deeptof_Data(Dataset):
	def __init__(self, args, train=True, transform=None):
		self.args = args
		if train == True:
			self.fdm, self.parameters, self.tdm = loadDeeptofTrainingData(self.args)
		else:
			self.fdm, self.parameters, self.tdm = loadDeeptofTestData(self.args)
		self.data_size = len(self.parameters)
		self.transform = transform

	def __getitem__(self, index):
		return (self.fdm[index], self.parameters[index], self.tdm[index])

	def __len__(self):
		return self.data_size