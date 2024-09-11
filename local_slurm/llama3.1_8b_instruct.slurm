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

# Wait for the server to start (adjust sleep time if needed)
sleep 10

# Print information about how to access the API
echo "API server is running on node $(hostname)"
echo "To access the API from della-vis1, use the following command:"
echo "1. Determine a port (<port>) on your local machine with 'get_free_port'"
echo "2. Run the following command on your local machine:"
echo "ssh -N -L localhost:<port>:$(hostname):8000 $(whoami)@$(hostname)"
echo "Then, you can access the API at http://localhost:<port>/v1"

# Keep the script running
wait





# Setting Up a Local Inference API for Open LLMs on Princeton's Della Cluster

This guide will walk you through setting up a local inference API for open-source large language models (LLMs) on the Della cluster. This allows you to run LLMs locally and query them just as you would normally use commercial APIs. We'll cover how to start the API server, connect to it, and use it for running language model inferences.

## Starting the API

To begin, you'll need to start an inference server for the model you want to use. We've created a Python script that simplifies this process by submitting the Slurm job and setting up the SSH port forwarding for you.

### Steps to Start the API:

1. Connect to Della using SSH:
   ```
   ssh <YourNetID>@della-vis1.princeton.edu
   ```

2. Navigate to the vLLM scripts directory:
   ```
   cd /scratch/gpfs/bs6865/vllm/
   ```

3. Run the Python script to submit the job and set up port forwarding. For example, to start a server that runs for 4 hours:
   ```
   python submit_vllm_job.py 4
   ```

   This script will:
   - Submit the Slurm job for the specified model
   - Wait for the job to start running
   - Set up SSH port forwarding from a free local port to the remote port on the compute node
   - Display information about how to access the API, including example Python and curl commands

4. The script will output colorized information about the job submission, SSH port forwarding, and how to use the API. It will look similar to this:

   ```
   Submitting Slurm job with runtime of 4 hours...
   Job submitted with ID: 12345
   Waiting for job to start...
   Job is now running
   Job is running on node: della-l05g6
   Setting up SSH port forwarding from local port 54321 to remote port 8000 on della-l05g6

   API is now available at: http://localhost:54321/v1
   You can now use this endpoint in your code to interact with the API.

   The server will run for approximately 4 hours.

   Here are examples of how to use the API:

   Python Example:
   from openai import OpenAI
   client = OpenAI(
       base_url="http://localhost:54321/v1",
       api_key="token-abc123",
   )

   completion = client.chat.completions.create(
     model="meta-llama/Meta-Llama-3.1-8B-Instruct",
     messages=[
       {"role": "system", "content": "Respond friendly to the user."},
       {"role": "user", "content": "Hello World!"}
     ]
   )
   print(completion.choices[0].message)

   Curl Example:
   curl http://localhost:54321/v1/chat/completions \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer token-abc123" \
     -d '{
       "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
       "messages": [
         {"role": "system", "content": "Respond friendly to the user."},
         {"role": "user", "content": "Hello World!"}
       ]
     }'

   Press Ctrl+C to stop the SSH port forwarding and exit.
   ```

5. You can now use the provided API endpoint in your code to interact with the model. The SSH port forwarding will remain active until you press Ctrl+C to exit the script.

## Using the API

Once your server is running and the SSH port forwarding is set up, you can send queries to the model using the provided endpoint. You can use either the Python example or the curl command provided in the script output to test the API.

Remember to replace the port number in the examples with the one provided by the script, as it will be dynamically assigned to avoid conflicts.

