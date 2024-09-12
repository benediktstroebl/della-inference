from omegaconf import DictConfig
import hydra
from jinja2 import Template
import os

base_path = None # if base_path is None will use folder structure from git repo.
model_name = 'llama3.1_8b_instruct'

implemented_models = [
    'llama3.1_8b_instruct',
    'llama3.1_70b_instruct',
    'phi3_medium_128k_instruct',
    'phi3_mini_128k_instruct'
]

model_name_to_hf = {
    'llama_3.1_8b_instruct': 'meta-llama/Meta-Llama-3.1-8B-Instruct',
    'llama3.1_70b_instruct': 'meta-llama/Meta-Llama-3.1-70B-Instruct',
    'phi3_medium_128k_instruct': 'microsoft/Phi-3-medium-128k-instruct',
    'phi3_mini_128k_instruct': 'microsoft/Phi-3-mini-128k-instruct'
}

hf_to_model_name = {v: k for k, v in model_name_to_hf.items()}

if model_name not in implemented_models:
    raise NotImplementedError('model not implemented, either update list or choose different model name.')

def convert_yaml_to_slurm(cfg: DictConfig):
    azure = cfg['azure']

    if azure:
        slurm_path = os.path.join(cfg['slurm_dir'], cfg['slurm_azure_fname'])
    else:
        slurm_path = os.path.join(cfg['slurm_dir'], cfg['slurm_fname'])

    with open(slurm_path, 'r') as f:
        slurm_file = f.read()

    template = Template(slurm_file)
    slurm_script = template.render(**cfg['model_configs'])

    return slurm_script, slurm_path

# just for testing
@hydra.main(version_base=None, config_path='.', config_name='config')
def main(cfg: DictConfig):
    print(convert_yaml_to_slurm(cfg))


if __name__ == '__main__':
    main()


