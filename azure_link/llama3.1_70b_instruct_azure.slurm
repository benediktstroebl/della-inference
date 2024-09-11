#!/usr/bin/env bash

#SBATCH --job-name=vllm_llama_3.1_70b
#SBATCH --output=vllm-llama-3.1-70b-%j.log
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=12:00:00
#SBATCH --cpus-per-gpu=12
#SBATCH --gres=gpu:4
#SBATCH --mem-per-gpu=16G
#SBATCH --constraint=gpu80
#SBATCH --mail-type=fail
#SBATCH --mail-user=stroebl@princeton.edu

module purge
module load anaconda3/2023.9
conda activate vllm

export HF_HUB_OFFLINE=1
export HF_HOME="/scratch/gpfs/bs6865/della-inference/_models"

# Start vllm serve in the background and establish port forwarding to platform-master Azure VM
vllm serve meta-llama/Meta-Llama-3.1-70B-Instruct --tensor-parallel-size 4 & ssh -i ~/.ssh/platform-master_key.pem -J bs6865@della-vis1 -R 51.8.97.78:6778:localhost:8000 -T -o BatchMode=yes azureuser@51.8.97.78 "echo 'SSH tunnel established'; sleep infinity" & wait