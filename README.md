# Description

This repository contains the code for a layer-2 DAPP (Decentralized Application) on top of ethereum blockchain using solidity. The DAPP is a simple 
application that allows users to create joint accounts and transfer funds between them. 
This DAPP is meant to implement transactions in a lightning network. The smart contract is deployed using truffle and ganache. Also a
client.py file is provided to interact with the smart contract. The client.py file is used to register users, create joint
accounts, transfer funds between users and joint accounts. The client.py file finally displays the number of successful
transactions and the number of failed transactions.

# Details

1. The folder `contracts` contains the code for a smart contract. 
2. People can join the lightening network, creating account in pairs.
3. When transaction has to take place between two people, the smart contract automatically finds out the shortest feasible route to do so (in the network of joint accounts), and transfers the amount
4. If no such path exists, then the smart contract shows an error.

# Instructions for running

1. Install `truffle and ganache`
2. Clone the repository 
3. Open a terminal in the source directory and run the following commands: 
  - `ganache`
  - `truffle migrate`
  - `python3 client.py` ( *Before running this command, make sure that the smart contract address is correct in client.py* )

You can pass the following arguments to client.py (All arguments are optional)
1. `-n or --num_nodes` : Number of users to register (Default: 100)
2. `-t or --num_transactions` : Number of transactions to perform (Default: 1000)
3. `-v or --mean_value` : Mean value of balance of the combined accounts of all users (Drawn from an exponential distribution) (Default: 10)
4. `-m or --m` : A parameter for the power law graph (Big m means more edges) (Default: 1)
5. `-a or --amount` : The amount to be transferred between users for each transaction (Default: 1)
6. `-s or --show` : Show the graph of the network

# Example
`python3 client.py -n 50 -t 400 -v 5 -m 2 -a 1 -s`

# Results

All the insights regarding the experiments run on the simulations done, are mentioned in `reposrt.pdf` file
