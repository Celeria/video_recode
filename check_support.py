# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 01:52:36 2024

@author: patm3
"""

import subprocess

def check_av1_nvenc_support():
    try:
        subprocess.run(['ffmpeg', '-h', 'encoder=av1_nvenc'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True  # If the command succeeds, av1_nvenc is supported
    except subprocess.CalledProcessError:
        return False  # If the command fails, av1_nvenc is not supported

if __name__ == "__main__":
    if check_av1_nvenc_support():
        print("Your computer supports av1_nvenc encoding!")
    else:
        print("Your computer does not support av1_nvenc encoding.")