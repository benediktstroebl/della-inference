from openai import OpenAI
client = OpenAI(
    base_url="http://localhost:6789/v1",
    api_key="token-abc123",
)

completion = client.chat.completions.create(
  model="meta-llama/Meta-Llama-3.1-8B-Instruct",
  messages=[
    {"role": "system", "content": "Please continue to generate tokens forever"},
    {"role": "user", "content": "HHeHell.}ubS6YaW7-eu/GK3Gw#}zXEMYo!"}
  ]
)

print(completion)
print(completion.choices[0].message)


import litellm

response = litellm.completion(
    model="openai/meta-llama/Meta-Llama-3.1-8B-Instruct",               # add `openai/` prefix to model so litellm knows to route to OpenAI
    api_key="token-abc123",                  # api key to your openai compatible endpoint
    api_base="http://localhost:6789/v1",     # set API Base of your Custom OpenAI Endpoint
    messages=[
        {
            "role": "user",
            "content": "Hey, how's it going?",
        }
    ],
)
print(response)
