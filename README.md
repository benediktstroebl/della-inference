# Setting Up a Local Inference API for Open LLMs on Princeton's Della Cluster

This guide will walk you through setting up a local inference API for open-source large language models (LLMs) on the Della cluster. This allows you to run LLMs locally and query them just as you would normally use commerical APIs. We'll cover how to start the API server, connect to it, and use it for running language model inferences.

## Context

### What is vLLM?

[vLLM](https://docs.vllm.ai/en/latest/index.html) is an open-source library for LLM inference and serving. It's designed to be fast and memory-efficient, and takes care of most of the inference hacks allowing for better utilization of GPU resources when running large language models. [vLLM supports various models](https://docs.vllm.ai/en/latest/models/supported_models.html), can be extended easily, and provides an API that's compatible with OpenAI's API, making it easier to integrate with existing workflows as well as LiteLLM.

### What is Slurm?

Slurm is a workload manager used on many computing clusters, including Della. It's responsible for allocating computational resources to users, scheduling jobs, and managing the cluster workload. Della's compute nodes are governed by Slurm, meaning that we can only run code through Slurm jobs that we need to schedule using **.slurm** files. For more details and examples for how these Slurm files look like [see the Della documentation](https://researchcomputing.princeton.edu/support/knowledge-base/slurm).

### File Storage on Della

Understanding the different storage options on Della is crucial for managing your data and running jobs efficiently. Here are the main directories you'll be working with:

#### Home Directory (/home/<YourNetID>)

- **Purpose**: Permanent storage for your personal files, scripts, and small datasets.
- **Quota**: Typically 50 GB (check current limits with the `checkquota` command).
- **Backup**: Yes, regularly backed up.

#### Scratch Space (/scratch/gpfs/<YourNetID>)

- **Purpose**: Large storage for datasets, code, and results (your main working drive).
- **Quota**: Much larger than home directory, often several TB (check with `checkquota`).
- **Backup**: No, data is not backed up.

#### Project Space (/projects/<project_name>)

- **Purpose**: Shared storage for project teams.
- **Quota**: Varies by project.
- **Backup**: Yes, but less frequently than home directories.

## Starting the API

To begin, you'll need to start an inference server for the model you want to use. If you use the Slurm scripts I set up so far, this server will run for 24 hours by default but you can set a different time very easily.

### Steps to Start the API:

1. Connect to Della using SSH:
   ```
   ssh <YourNetID>@della-vis1.princeton.edu
   ```

2. Navigate to the vLLM scripts directory:
   ```
   cd /scratch/gpfs/bs6865/vllm/
   ```

   **Note:** You should have read and execute permissions on the files in this directory.

3. Find the Slurm script for your desired model and submit it as a job. For example, to use Meta's Llama3.1 8B Instruct model:
   ```
   sbatch /scratch/gpfs/bs6865/vllm/llama3.1_8b_instruct.slurm
   ```

This command submits a job to Slurm, which will start a vLLM server on a GPU node of Della with the necessary resources to host the model as specified in the Slurm script.

## Using the API

Once your server is running, you can send queries to the model. You have two options for connecting to the API:

### Option 1: Running queries from Della directly

1. Find which GPU node is running your server:
   ```
   squeue -u <your netid>
   ```

2. SSH into that GPU node using port forwarding:
   ```
   ssh -N -L localhost:<choose a free port>:<node_name>:8000 bs6865@<node_name>
   ```
   For example: 
   ```
   ssh -N -L localhost:4567:della-l05g6:8000 bs6865@della-l05g6
   ```

    **To check whether a port is free run:**
    ```
    lsof -i :<port_number>
    ```

    If this command returns not output then the port you tested is free.

    **Note:** This will keep the terminal session you ran it in occupied as long as the SSH tunnel is open. This is on purpose becuase it prevents us from creating more and more port forwardings without noticing. As soon as you exit the terminal, the connection will be closed. 

   What is port forwarding?
   Port forwarding is a technique that allows you to create a secure tunnel between your local machine and a remote server. In this case, it's used to access the API running on a Della GPU node from the login node you land in when use ssh into Della.

3. You can now run inference using Python code executed on the Della node you ran step 1-3 on (see examples below). As mention in the Note, you need to open a new terminal window to navigate on the node given that the first window is keeping the SSH tunnel open.

### Option 2: Using Azure VM

If you're using the **platform-master** Azure VM, you can connect to the API using the endpoint:
```
http://localhost:<model port>/v1
```

The model ports are set in the Slurm script. Check the Model-Ports Table in the full documentation for the correct port number. The **platform-master** VM is set up by us on Azure. We use this VM to run all evaluations for HAL. This is because we want to standardize hardware but also because Della does not support Docker out-of-the-box. Given that many evaluation harnesses of benchmarks use Docker, we opted to use Azure over Della for running evaluations. 

However, we can still use the inference API hosted on Della and query it from the Azure VM as if it would be available as an API on the internet using SSH and port forwarding again. The necessary connection is established automatically in the Slurm scripts I provided so once the Slurm job has started, we are ready to go.

#### Model Ports on Azure VM

When accessing the API from the platform-master Azure VM, each model is assigned a specific port. Use these ports when constructing your API endpoint URL. Here's a table of the current model-to-port mappings:

| Model | Port |
|-------|------|
| meta-llama/Meta-Llama-3.1-8B-Instruct | 6789 |
| meta-llama/Meta-Llama-3.1-70B-Instruct | 6778 |

To use a specific model, your API endpoint URL should be:

```
http://localhost:<port from table above>/v1
```

For example, to use the Meta-Llama-3.1-8B-Instruct model, your endpoint would be:

```
http://localhost:6789/v1
```

Remember to use these ports in your code when initializing the API client. For instance:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:6789/v1",  # For Meta-Llama-3.1-8B-Instruct
    api_key="token-abc123",
)
```

Note: These port assignments are set in the Slurm scripts. If you modify the scripts or add new models, make sure to update this table accordingly. Always use a unique port for each model to avoid conflicts. Right now, if two people were to start an inference server for the same model, the second server would run into the issue that the port to the Azure VM is already occupied. We can fix this with some dynamic scheme at some point but given that the same model will be available under the port, it should not keep us from using the same model simultaneously.


## Code Examples

Here are two ways to interact with the API using Python:

### 1. Using LiteLLM

LiteLLM is a library that provides a unified interface for different LLM providers.

```python
import litellm

# Set up the API call
response = litellm.completion(
    model="openai/meta-llama/Meta-Llama-3.1-8B-Instruct",  # Model name with 'openai/' prefix
    api_key="token-abc123",  # Any string will work as the API key
    api_base="http://localhost:6789/v1",  # API endpoint (adjust port as needed)
    messages=[
        {"role": "user", "content": "Hey, how's it going?"},  # Your input to the model
    ]
)

# Print the model's response
print(response)
```

### 2. Using OpenAI Client

The OpenAI client is a Python library for interacting with OpenAI-compatible APIs.

```python
from openai import OpenAI

# Initialize the client
client = OpenAI(
    base_url="http://localhost:6789/v1",  # API endpoint (adjust port as needed)
    api_key="token-abc123",  # Any string will work as the API key
)

# Make a request to the model
completion = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct",  # Model name
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},  # Optional system message
        {"role": "user", "content": "What is the capital of France?"}  # Your question
    ]
)

# Print the model's response
print(completion.choices[0].message)
```

## Additional Notes

- I did not develop this as a tool so far so we can think about what makes sense in terms of shared directories to store models, CLI arguments to customize Slurm scripts etc. 
- This should give a complete example of how to set up an inference server and use it on Della. It should now be easy to do the same for a new model and using your own directories. 
