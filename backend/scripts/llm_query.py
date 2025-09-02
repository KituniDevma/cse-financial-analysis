# llm_query.py: LLM agent for querying the dataset

import pandas as pd
from langchain.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
import os

os.environ['OPENAI_API_KEY'] = 'your-openai-key-here'  # Replace with your key

llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
df = pd.read_csv('../data/clean_dataset.csv')
agent = create_pandas_dataframe_agent(llm, df, verbose=True, handle_parsing_errors=True)