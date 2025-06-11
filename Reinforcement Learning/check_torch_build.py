import torch
print(f"PyTorch version: {torch.__version__}")
print(f"PyTorch built with CUDA: {torch.backends.cudnn.enabled if hasattr(torch.backends, 'cudnn') else 'No CUDA build'}")
