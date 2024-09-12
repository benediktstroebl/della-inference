#!/usr/bin/env bash

#SBATCH --job-name=vllm_phi_3_small_128k_instruct
#SBATCH --output=vllm-phi_3_small_128k_instruct-%j.log
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=24:00:00
#SBATCH --cpus-per-gpu=12
#SBATCH --gres=gpu:2
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
vllm serve microsoft/Phi-3-small-128k-instruct --tensor-parallel-size 2 --trust-remote-code & ssh -i ~/.ssh/platform-master_key.pem -J bs6865@della-vis1 -R 51.8.97.78:27260:localhost:8000 -T -o BatchMode=yes azureuser@51.8.97.78 "echo 'SSH tunnel established'; sleep infinity" & wait