from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv

load_dotenv()
model_name = "anthropic/claude-opus-4.5"  # Replace with your desired model name

llm = ChatOpenAI(
    api_key=getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model=model_name,
    # default_headers={
    #     "HTTP-Referer": getenv("YOUR_SITE_URL"),  # Optional. Site URL for rankings on openrouter.ai.
    #     "X-Title": getenv("YOUR_SITE_NAME"),  # Optional. Site title for rankings on openrouter.ai.
    # }
)

# Example usage
prompt_1 = "Tell me a joke about computers."
prompt_2 = "What NFL team won the Super Bowl in the year Justin Bieber was born?"
prompt_3 = "Write a poem about the ocean."


prompts_list = [prompt_1, prompt_2, prompt_3]

for prompt in prompts_list:
    response = llm.invoke(prompt)
    #Format question and answer, print them
    

    print(f"Q: {prompt}\nA: {response.content}\n")

