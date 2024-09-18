from omegaconf import DictConfig
import hydra
from jinja2 import Template
import os

def convert_yaml_to_slurm(cfg: DictConfig):
    use_azure = cfg['use_azure']

    if use_azure:
        slurm_path = os.path.join(cfg['slurm_dir'], cfg['slurm_azure_fname'])
    else:
        slurm_path = os.path.join(cfg['slurm_dir'], cfg['slurm_fname'])

    with open(slurm_path, 'r') as f:
        slurm_file = f.read()

    template = Template(slurm_file)
    slurm_script = template.render(**cfg['model_configs'])

    use_pli = cfg['use_pli']
    if use_pli:
        list_slurm = slurm_script.split('\n')
        list_slurm.insert(3, '#SBATCH --partition=pli')
        list_slurm.insert(4, '#SBATCH --account=hal')
        slurm_script = '\n'.join(list_slurm)
    return slurm_script, slurm_path

# just for testing
@hydra.main(version_base=None, config_path='.', config_name='config')
def main(cfg: DictConfig):
    convert_yaml_to_slurm(cfg)


if __name__ == '__main__':
    main()


