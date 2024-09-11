#!/usr/bin/env bash

#SBATCH --job-name=vllm_llama_3.1_8b
#SBATCH --output=vllm-llama-3.1-8b-%j.log
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
vllm serve meta-llama/Meta-Llama-3.1-8B-Instruct --tensor-parallel-size 2 &


# Keep the script running
wait

