# Setting Up a Local Inference API for Open LLMs on Princeton's Della Cluster

This guide will walk you through setting up a local inference API for open-source large language models (LLMs) on the Della cluster. This allows you to run LLMs locally and query them just as you would normally use commerical APIs. We'll cover how to start the API server, connect to it, and use it for running language model inferences.

## Context

### What is vLLM?

[vLLM](https://docs.vllm.ai/en/latest/index.html) is an open-source library for LLM inference and serving. It's designed to be fast and memory-efficient, and takes care of most of the inference hacks allowing for better utilization of GPU resources when running large language models. [vLLM supports various models](https://docs.vllm.ai/en/latest/models/supported_models.html), can be extended easily, and provides an API that's compatible with OpenAI's API, making it easier to integrate with existing workflows as well as LiteLLM.

### What is Slurm?

Slurm is a workload manager used on many computing clusters, including Della. It's responsible for allocating computational resources to users, scheduling jobs, and managing the cluster workload. Della's compute nodes are governed by Slurm, meaning that we can only run code through Slurm jobs that we need to schedule using **.slurm** files. For more details and examples for how these Slurm files look like [see the Della documentation](https://researchcomputing.princeton.edu/support/knowledge-base/slurm).

### File Storage on Della

Della has different file storage spaces that are connected to **all** nodes and mainly differ in their capacity and whether they have a backup or not. Here are the main spaces you'll be working with:

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

## Supported Models

This inference API currently supports the following models:

| Model Name| Hugging Face Link |
|------------|-------------------|
| Meta Llama-3.1-70B-Instruct | [🤗 Model](https://huggingface.co/meta-llama/Meta-Llama-3.1-70B-Instruct) |
| Meta Llama-3.1-8B-Instruct | [🤗 Model](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct) |
| microsoft/Phi-3-mini-128k-instruct | [🤗 Model](https://huggingface.co/microsoft/Phi-3-mini-128k-instruct) |
| microsoft/Phi-3-medium-128k-instruct | [🤗 Model](https://huggingface.co/microsoft/Phi-3-medium-128k-instruct) |

To request support for additional models, please open an issue or submit a pull request.

## Setup

1. Clone this repository
    ```
    git clone https://github.com/benediktstroebl/della-inference.git
    cd della-inference
    ```

2. Load the Anaconda module if not yet loaded:
   ```
   module load anaconda3/2023.9
   ```

3. Create a new conda environment (please keep using `vllm` as the env name):
   ```
   conda create -n vllm python=3.10 -y
   ```

4. Activate the new environment:
   ```
   conda activate vllm
   ```

5. Install the required packages using pip and the requirements.txt file:
   ```
   pip install -r requirements.txt
   ```


## Starting the API

To begin, you'll need to start an inference server for the model you want to use.

### Option 1: Running queries from Della directly

1. Connect to Della using SSH:
   ```
   ssh <YourNetID>@della-vis1.princeton.edu
   ```

2. Edit config file to determine which job you want to run.

`config.yaml` looks like, this is where you'll be defining which model you want to use and how long to set it up for.

```yaml
defaults:
  - model_configs: Meta-Llama-3.1-8B-Instruct #Meta-Llama-3.1-8B-Instruct, Meta-Llama-3.1-70B-Instruct, Phi-3-mini-128k-instruct, Phi-3-medium-128k-instruct

# determine if you want to run it on Azure (changes slurm)
azure: True
# how many hours to run for
time: 1


# most likely ignore (edit only if you change templates)
slurm_dir: templates
slurm_fname: slurm_template.txt
slurm_azure_fname: slurm_azure_template.txt
```


3. Run the Python script to submit the job and set up port forwarding. For example, to start a server that runs for 4 hours:
   ```
   python run.py
   ```

   This script will:
   - Submit the Slurm job for the specified model
   - Wait for the job to start running
   - Set up SSH port forwarding from a free local port to the remote port on the compute node
   - Display information about how to access the API, including an example curl command to try out the API in the terminal. Other examples are included in `example_inference_calls.py`

Note that [hydra](https://hydra.cc/) (the software we use to setup configs) also lets you adjust parameters from the command line. [Here](https://hydra.cc/docs/advanced/override_grammar/basic/) is there basic override syntax.

In other words, you can run it like this: 

   ```
   python run.py model_configs=Phi-3-mini-128k-instruct ++time=12 
   ```

This will change the model to `Phi-3 mini` and keep the server running for 12 hours. 

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

   =====
   TRY IT OUT AND PASTE THE FOLLOWING IN A TERMINAL WINDOW:
   
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
   =====

   Press Ctrl+C to stop the SSH port forwarding and exit.
   ```
   **What is port forwarding?**
   Port forwarding is a technique that allows you to create a secure tunnel between your local machine and a remote server. In this case, it's used to access the API running on a Della GPU node from the login node you land when you ssh into Della.

5. You can now use the provided API endpoint in your code to interact with the model. The SSH port forwarding will remain active until you press Ctrl+C to exit the script. Note that the job will keep running and you can open a new ssh connection to access the API again. If you want to end the job, please do so via, e.g., your MyDella dashboard.

6. Note, in case you accidentally close the port forwarding simply run 

```sh
ssh -N -L localhost:{local_port}:{node}:{remote_port} {username}@{node}
```

Where `local_port` can be anything, `node` is your gpu node, `remote_port` is 8000, and `username` is your NetID. 


#### Using the API

Once your server is running and the SSH port forwarding is set up, you can send queries to the model using the provided endpoint. You can use either the Python example or the curl command provided in the script output to test the API.

### Option 2: Using Azure VM (only relevant for our group)

If you're using the **platform-master** Azure VM, you can connect to the API using the endpoint:
```
http://localhost:<model port>/v1
```

This will be available after simply running the Slurm job for the respective model in:
```
/scratch/gpfs/bs6865/della-inference/azure_link
```

If you use the Slurm scripts I set up so far, this server will run for 24 hours by default but you can set a different time very easily by modifying the options in the header of the Slurm scripts.

**Note:** This model port is different from the one you set if you query the API from Della directly (Option 1) and apply only for the Azure VM. Read further for more details.

The model ports are set in the Slurm script. Check the model ports table below for the correct port number. The **platform-master** VM is set up by us on Azure (platform-master is simply the name of the VM we set). We use this VM to run all evaluations for HAL. This is because we want to standardize hardware but also Della does not support Docker out-of-the-box. Given that many evaluation harnesses of benchmarks use Docker, we opted to use Azure over Della for running evaluations. 

However, we can still use the inference API hosted on Della and query it from the Azure VM as if it would be available as an API on the internet using SSH and port forwarding again. The necessary connection is established automatically in the Slurm scripts I provided so once the Slurm job has started, we are ready to go.

#### Model Ports on Azure VM

When accessing the API from the platform-master Azure VM, each model is assigned a specific port. Use these ports when constructing your API endpoint URL. Here's a table of the current model-to-port mappings:

| Model | Port |
|-------|------|
| meta-llama/Meta-Llama-3.1-8B-Instruct | 6789 |
| meta-llama/Meta-Llama-3.1-70B-Instruct | 6778 |
| microsoft/Phi-3-mini-128k-instruct | 33986 |
| microsoft/Phi-3-small-128k-instruct | 27260 |
| microsoft/Phi-3-medium-128k-instruct | 35250 |

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

## Adding models

If you want to add new models please add a pull request and I will add them.

## Additional Notes

- I did not develop this as a tool so far so we can think about what makes sense in terms of shared directories to store models, CLI arguments to customize Slurm scripts etc. 
- This should give a complete example of how to set up an inference server and use it on Della. It should now be easy to do the same for a new model and using your own directories. 
