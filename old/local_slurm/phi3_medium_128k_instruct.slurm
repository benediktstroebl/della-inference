#!/usr/bin/env bash

#SBATCH --job-name=vllm_phi_3_medium_128k_instruct
#SBATCH --output=vllm-phi_3_medium_128k_instruct-%j.log
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=12:00:00
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

# Find a free port
FREE_PORT=$(get_free_port)

# Start vllm serve
vllm serve microsoft/Phi-3-medium-128k-instruct --tensor-parallel-size 2 &


# Keep the script running
wait

