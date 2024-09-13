from omegaconf import DictConfig
import hydra
from jinja2 import Template
import os

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


