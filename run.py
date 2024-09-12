import subprocess
import time
import re
import os
import argparse
from pathlib import Path
import hydra
from omegaconf import DictConfig

from utils import convert_yaml_to_slurm

curr_file_path = Path(__file__).resolve()

def submit_slurm_job(slurm_script: str, runtime: str, slurm_path: str):

    # Modify the runtime in the script
    modified_script = re.sub(r'#SBATCH --time=\d{2}:\d{2}:\d{2}', f'#SBATCH --time={runtime}:00:00', slurm_script)
    # Write the modified script to a temporary file
    temp_script = slurm_path.replace('.txt', '.temp')
    with open(temp_script, 'w') as file:
        file.write(modified_script)

    # Submit the job and get the job ID
    result = subprocess.run(['sbatch', temp_script], capture_output=True, text=True)

    # Remove the temporary file
    os.remove(temp_script)

    job_id = re.search(r'Submitted batch job (\d+)', result.stdout)

    try:
        return job_id.group(1)
    except Exception as e:
        raise Exception(f'Failed to submit job - {e}')


def get_job_status(job_id):
    result = subprocess.run(['squeue', '-j', job_id, '-h', '-o', '%t'], capture_output=True, text=True)
    return result.stdout.strip()


def get_job_node(job_id):
    result = subprocess.run(['squeue', '-j', job_id, '-h', '-o', '%N'], capture_output=True, text=True)
    return result.stdout.strip()


def get_free_port():
    result = subprocess.run(['get_free_port'], capture_output=True, text=True)
    return result.stdout.strip()


def setup_ssh_port_forwarding(node, remote_port, local_port):
    username = os.getenv('USER')
    ssh_command = f"ssh -N -L localhost:{local_port}:{node}:{remote_port} {username}@{node}"
    print(f"Setting up SSH port forwarding with command: {ssh_command}")
    return subprocess.Popen(ssh_command, shell=True)


def print_usage_examples(port):
    print("\n=====\nTRY IT OUT AND PASTE THE FOLLOWING IN A TERMINAL WINDOW:")
    #     python_example = f"""
    # Python Example:
    # from openai import OpenAI
    # client = OpenAI(
    #     base_url="http://localhost:{port}/v1",
    #     api_key="token-abc123",
    # )

    # completion = client.chat.completions.create(
    #   model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    #   messages=[
    #     {{"role": "system", "content": "Respond friendly to the user."}},
    #     {{"role": "user", "content": "Hello World!"}}
    #   ]
    # )
    # print(completion.choices[0].message)
    # """

    curl_example = f"""
curl http://localhost:{port}/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer token-abc123" \\
  -d '{{
    "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "messages": [
      {{"role": "system", "content": "Respond friendly to the user."}},
      {{"role": "user", "content": "Hello World!"}}
    ]
  }}'
"""

    # print(python_example)
    print(curl_example)
    print("=====\n\n")


@hydra.main(version_base=None, config_path='.', config_name='config')
def main(cfg: DictConfig):
    time_ = cfg['time']
    slurm_script, slurm_path = convert_yaml_to_slurm(cfg)

    print(f"Submitting Slurm job with time of {time_} hours...")
    job_id = submit_slurm_job(slurm_script, time_, slurm_path)
    print(f"Job submitted with ID: {job_id}")

    print("Waiting for job to start...")
    while get_job_status(job_id) != 'R':
        time.sleep(5)

    print("Job is now running")
    node = get_job_node(job_id)
    print(f"Job is running on node: {node}")

    print("Wating for API to start...")
    time.sleep(30)  # Wait for the API to start
    print("API server should now be running")

    local_port = get_free_port()
    remote_port = '8000'  # This is the port vLLM uses by default

    print(f"Setting up SSH port forwarding from local port {local_port} to remote port {remote_port} on {node}")
    ssh_process = setup_ssh_port_forwarding(node, remote_port, local_port)

    print(f"\nAPI is now available at: http://localhost:{local_port}/v1")
    print("You can now use this endpoint in your code to interact with the API.")
    print(f"\nThe server will run for approximately {time_} hours.")

    print_usage_examples(local_port)

    print("\nPress Ctrl+C to stop the SSH port forwarding and exit.")

    try:
        ssh_process.wait()
    except KeyboardInterrupt:
        print("\nStopping SSH port forwarding and exiting...")
        ssh_process.terminate()


if __name__ == "__main__":
    main()