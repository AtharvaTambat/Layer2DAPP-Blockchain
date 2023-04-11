# DESCRIPTION

The aim of this assignment was to build a layer-2 DAPP on top of ethereum blockchain using solidity. The DAPP is a simple 
application that allows users to create joint accounts and transfer funds between them. This application is meant to
mimic the functionality of a lightning network. The smart contract is deployed using truffle and ganache. Also a
client.py file is provided to interact with the smart contract. The client.py file is used to register users, create joint
accounts, transfer funds between users and joint accounts. The client.py file finally displays the number of successful
transactions and the number of failed transactions.

# INSTRUCTIONS

1. Install `truffle and ganache`
2. Clone the repository 
3. Open a terminal in the source directory and run the following commands:
  -`ganache`
  -`truffle migrate`
  -`python3 client.py`

You can pass the following arguments to client.py (All arguments are optional)
1. `-n or --num_nodes` : Number of users to register (Default: 100)
2. `-t or --num_transactions` : Number of transactions to perform (Default: 1000)
3. `-v or --mean_value` : Mean value of balance of the combined accounts of all users (Drawn from an exponential distribution) (Default: 10)
4. `-m or --m` : A parameter for the power law graph (Big m means more edges) (Default: 1)
5. `-a or --amount` : The amount to be transferred between users for each transaction (Default: 1)
6. `-s or --show` : Show the graph of the network

# EXAMPLE
`python3 client.py -n 50 -t 400 -v 5 -m 2 -a 1 -s`
