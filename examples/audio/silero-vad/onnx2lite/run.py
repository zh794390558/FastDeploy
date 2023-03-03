#!/usr/bin/env python3
import argparse
from x2paddle.convert import pytorch2paddle
import torch

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--jit-path', default=None, type=str)
  parser.add_argument('--save-path', default=None, type=str)
  args = parser.parse_args()
  print(args)

  moduble = torch.jit.load(args.jit_path)
  save_dir = args.save_path

  pytorch2paddle(
        module, 
        save_dir, 
        jit_type="trace", 
        input_examples=None, 
        convert_to_lite=True, 
        lite_valid_places="arm", 
        lite_model_type="naive_buffer"
  )
