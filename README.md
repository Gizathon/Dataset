Rugpull Prediction Dataset Preparation
Overview
This project is designed to collect and process data for the purpose of predicting rugpull events in cryptocurrency markets. The dataset is built by querying blockchain data using The Graph protocol and processing it to ensure scam tokens are correctly identified and normalized.

Pair.py
Contents
switch_token(result): A function to ensure scam tokens are consistently marked as token0.
run_query(query): A function to execute GraphQL queries against The Graph endpoint.
GraphQL queries to fetch pair data from a specified subgraph.
Data collection loop to iterate through all available pairs and process them.
Data normalization and saving to CSV.
Requirements
Python 3.6 or higher
Required Python packages:
requests
pandas
beautifulsoup4
Install the required packages using pip:

sh
Copy code
pip install requests pandas beautifulsoup4
Functions
switch_token(result)
This function takes the result of a query and ensures that the token with more transactions is always listed as token0. This normalization helps in identifying scam tokens more consistently.

Parameters:

result (dict): The result from a GraphQL query containing token pair data.
Returns:

None
run_query(query)
This function sends a GraphQL query to The Graph endpoint and returns the result.

Parameters:

query (str): The GraphQL query to be executed.
Returns:

dict: The JSON response from the endpoint.
Raises:

Exception: If the query fails or returns a status code other than 200.
Usage
The script is designed to be run as a standalone script. It initializes a query to fetch the latest token pairs, processes the results, and continues querying iteratively to gather more data.

Initial Query
The initial query (query_init) fetches the most recent token pairs. The results are processed to normalize token data using the switch_token function. Valid pairs (containing WETH tokens) are collected.

Iterative Queries
An iterative query template (query_iter_template) is used to fetch additional pairs created before the last block number obtained in the previous query. This loop continues until no more valid pairs are found or an error occurs.

Data Storage
Collected data is normalized and stored in a CSV file named temp.csv.

