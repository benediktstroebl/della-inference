import subprocess
import time
import re
import os
import argparse

def submit_slurm_job(slurm_script, runtime):
    # Read the original Slurm script
    with open(slurm_script, 'r') as file:
        script_contents = file.read()
    
    # Modify the runtime in the script
    modified_script = re.sub(r'#SBATCH --time=\d{2}:\d{2}:\d{2}', f'#SBATCH --time={runtime}:00:00', script_contents)
    
    # Write the modified script to a temporary file
    temp_script = f'{slurm_script}.temp'
    with open(temp_script, 'w') as file:
        file.write(modified_script)
    
    # Submit the job and get the job ID
    result = subprocess.run(['sbatch', temp_script], capture_output=True, text=True)
    
    # Remove the temporary file
    os.remove(temp_script)
    
    job_id = re.search(r'Submitted batch job (\d+)', result.stdout)
    if job_id:
        return job_id.group(1)
    else:
        raise Exception("Failed to submit job")

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


    curl_example = f"""
curl http://localhost:{port}/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer token-abc123" \\
  -d '{{
    "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
    "messages": [
      {{"role": "system", "content": "Respond friendly to the user."}},
      {{"role": "user", "content": "Hello World!"}}
    ]
  }}'
"""

    print(curl_example)
    print("=====\n\n")

def main():
    parser = argparse.ArgumentParser(description="Submit a Slurm job and set up SSH port forwarding for vLLM API")
    parser.add_argument("--time", type=int, help="Time for the Slurm job in hours")
    args = parser.parse_args()

    slurm_script = '/scratch/gpfs/bs6865/vllm/local_slurm/llama3.1_70b_instruct.slurm'  # Update this with your Slurm script name
    
    print(f"Submitting Slurm job with time of {args.time} hours...")
    job_id = submit_slurm_job(slurm_script, args.time)
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
    print(f"\nThe server will run for approximately {args.time} hours.")
    
    print_usage_examples(local_port)
    
    print("\nPress Ctrl+C to stop the SSH port forwarding and exit.")
    
    try:
        ssh_process.wait()
    except KeyboardInterrupt:
        print("\nStopping SSH port forwarding and exiting...")
        ssh_process.terminate()

if __name__ == "__main__":
    main()