from torch.utils.data import Dataset, DataLoader
import cv2
import os
import numpy as np
import random
import time

from torchvision import transforms
from utils import read_clip, show_flow, generate_motion_label, show_with_pattern, generate_app_label
from utils.video_transforms import RandomCrop, ToTensor


class ucf101(Dataset):
    def __init__(self, data_list, rgb_prefix, flow_x_prefix, flow_y_prefix,
                 motion_flag=(1,1,1,1), app_flag=(1,1,1,1), clip_len=16, rz_size=(128, 171), transforms=None):


        lines = open(data_list, 'r')
        self.lines = list(lines)

        self.rgb_prefix = rgb_prefix
        self.flow_x_prefix = flow_x_prefix
        self.flow_y_prefix = flow_y_prefix
        self.motion_flag = motion_flag
        self.app_flag = app_flag
        self.rz_size = rz_size
        self.clip_len = clip_len
        self.transforms = transforms


    def __len__(self):
        return len(self.lines)

    def __getitem__(self, index):

        line = self.lines[index].strip('\n').split()
        sample_name = line[0]
        start_frame = int(line[1])
        label = line[2]

        rgb_dir = self.rgb_prefix + sample_name
        flow_x_dir = self.flow_x_prefix + sample_name.split('/')[1]
        flow_y_dir = self.flow_y_prefix + sample_name.split('/')[1]

        clip_len = self.clip_len
        rz_size = self.rz_size

        rgb_clip = read_clip.load_rgb(rgb_dir, clip_len, start_frame, rz_size)
        flow_x_clip = read_clip.load_flow(flow_x_dir, clip_len, start_frame, rz_size)
        flow_y_clip = read_clip.load_flow(flow_y_dir, clip_len, start_frame, rz_size)

        sample = {'rgb_clip': rgb_clip, 'u_flow': flow_x_clip, 'v_flow': flow_y_clip}

        if self.transforms:
            sample = self.transforms(sample)

            sample = generate_motion_label.motion_statistics(self.motion_flag, sample)

            sample = generate_app_label.app_statistics(self.app_flag, sample)


        return sample


if __name__ == '__main__':
    data_list = 'D:/dataset/ucf101/list/ucf101_train.list'
    rgb_prefix = 'D:/dataset/ucf101/ucf101_jpegs_256/'
    flow_x_prefix = 'D:/dataset/ucf101/tvl1_flow/u/'
    flow_y_prefix = 'D:/dataset/ucf101/tvl1_flow/v/'


    transforms = transforms.Compose([RandomCrop(112),
                                     ToTensor()])
    ucf101_dataset = ucf101(data_list, rgb_prefix, flow_x_prefix, flow_y_prefix,
                                    transforms=transforms)

    sample_num = len(ucf101_dataset)
    print(sample_num)

    dataloader = DataLoader(ucf101_dataset, batch_size=1, shuffle=True, num_workers=1)

    s_time = time.time()
    for i_batch, sample_batched in enumerate(dataloader):
        print(i_batch)
        print("load data time:", time.time() - s_time)

        print(sample_batched['motion_label'])
        print(sample_batched['app_label'])

        print(sample_batched['motion_label'].shape)
        print(sample_batched['app_label'].shape)


        print("OK")
        s_time = time.time()


        #show_with_pattern.show(sample_batched)


    # for i in range(sample_num):
    #     sample = kinetics_400[i]
    #
    #     print(i)
    #
    #
    #     du_x_sum = sample['du']


        # for i in range(len(cur_rgb_clip)):
        #     rgb_img = cur_rgb_clip[i]
        #     cv2.imshow('img', rgb_img)
        #     cv2.waitKey()
        #
        #     flow_x_img = cur_flow_x_clip[i]
        #     flow_y_img = cur_flow_y_clip[i]
        #     flow_img = show_flow.computeImg(flow_x_img, flow_y_img)
        #     cv2.imshow('optical flow', flow_img)
        #     cv2.waitKey()



