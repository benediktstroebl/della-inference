from omegaconf import OmegaConf
from hydra import compose, initialize

try:
    config = initialize(config_path='.', job_name='test')
    cfg = compose(config_name='model_configs/llama3.1_8b_instruct.yaml')
except:
    cfg = compose(config_name='llama3.1_8b_instruct.yaml')

print(cfg)

# expected output:
    # {
        # 'job-name': 'vllm_llama_3.1_8b',
        # 'output': 'vllm-llama-3.1-8b-%j.log',
        # 'tensor-parallel-size': 2,
        # 'nodes': 1,
    # ...}
