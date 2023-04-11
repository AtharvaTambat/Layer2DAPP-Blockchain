import argparse
import json
import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from web3 import Web3

########################################################################################################################################################

# Parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('-n','--num_users', type=int, default=100, help='Number of nodes in the network')
parser.add_argument('-t','--num_transactions', type=int, default=1000, help='Number of transactions to be sent')
parser.add_argument('-v','--mean_value', type=int, default=10, help='Mean value of the combined balance of the two accounts')
parser.add_argument('-m','--m', type=int, default=1, help='Number of edges to attach from a new node to existing nodes')
parser.add_argument('-a','--amount', type=int, default=1, help='Amount to be sent in each transaction')
parser.add_argument('-s','--show', action = 'store_true' , help='Show the graph')

args = parser.parse_args()

# CONSTANTS
GAS_AMOUNT = 30000000 # 30 million gas
NUM_USERS = args.num_users # number of nodes in the network
NUM_TRANSACTIONS = args.num_transactions # number of transactions to be sent
MEAN_VALUE = args.mean_value     # mean value of the combined balance of the two accounts
m = args.m                       # a parameter for the power law graph
amount = args.amount # amount to be sent in each transaction

########################################################################################################################################################

#connect to the local ethereum blockchain
provider = Web3.HTTPProvider('http://127.0.0.1:8545')
w3 = Web3(provider)
w3.eth.handleRevert = True
#check if ethereum is connected
print(w3.is_connected())

#replace the address with your contract address (!very important)
deployed_contract_address = '0xe8502b69Fd7f7dF0eC01CE3ba35415B6E04Be6fe'

#path of the contract json file. edit it with your contract json file
compiled_contract_path ="build/contracts/DAPP.json"
with open(compiled_contract_path) as file:
    contract_json = json.load(file)
    contract_abi = contract_json['abi']
contract = w3.eth.contract(address = deployed_contract_address, abi = contract_abi)

########################################################################################################################################################

# CREATE THE NETWORK

G = nx.powerlaw_cluster_graph(NUM_USERS,m,0.5)
while not nx.is_connected(G):
    G = nx.powerlaw_cluster_graph(NUM_USERS,m,0.5)

# set the weights of the edges (the combined balance of the two accounts)
weights = {edge: max(int(np.random.exponential(scale=MEAN_VALUE)),1) for edge in G.edges}
nx.set_edge_attributes(G, values=weights, name='weight')

def display_graph(G):
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'))
    nx.draw_networkx_labels(G, pos)
    plt.show()

if args.show:
    display_graph(G)

########################################################################################################################################################

# REGISTER THE USERS
for i in range(NUM_USERS):
    user_id = i
    user_name = f"User_{i}"
    txn_receipt = contract.functions.registerUser(user_id,user_name).transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':GAS_AMOUNT})

    # fetch a reverted transaction:
    tx = w3.eth.get_transaction(txn_receipt)

    # build a new transaction to replay:
    replay_tx = {
        'to': tx['to'],
        'from': tx['from'],
        'value': tx['value'],
        'data': tx['input'],
    }

    # replay the transaction locally:
    try:
        w3.eth.call(replay_tx, tx.blockNumber - 1)
        print(f"User with user id: {user_id} and user name: {user_name} registered")
    except Exception as e:
        message = e.args[0]['message']
        print(message[message.find("revert ")+7:])

########################################################################################################################################################

# CREATE THE ACCOUNTS

for edge in G.edges:
    # create the account with half of the combined balance of the two accounts
    txn_receipt = contract.functions.createAcc(edge[0], edge[1], int(G.edges[edge]['weight']/2)).transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':GAS_AMOUNT})
    
    # fetch a reverted transaction:
    tx = w3.eth.get_transaction(txn_receipt)

    # build a new transaction to replay:
    replay_tx = {
        'to': tx['to'],
        'from': tx['from'],
        'value': tx['value'],
        'data': tx['input'],
    }

    # replay the transaction locally:
    try:
        w3.eth.call(replay_tx, tx.blockNumber - 1)
        print(f"Account created between {edge[0]} and {edge[1]} with combined balance {G.edges[edge]['weight']}")
    except Exception as e:
        message = e.args[0]['message']
        print(message[message.find("revert ")+7:])


########################################################################################################################################################

# SEND THE TRANSACTIONS

num_successful_transactions = []
successful_transactions = 0

for i in range(NUM_TRANSACTIONS):
    random_node_1 = random.randint(0,NUM_USERS-1) 
    random_node_2 = random.randint(0,NUM_USERS-1)
    while (random_node_1 == random_node_2):
        random_node_2 = random.randint(0,NUM_USERS-1)
    txn_receipt = contract.functions.sendAmount(random_node_1,random_node_2,amount).transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':GAS_AMOUNT})
    
    # fetch a reverted transaction:
    tx = w3.eth.get_transaction(txn_receipt)

    # build a new transaction to replay:
    replay_tx = {
        'to': tx['to'],
        'from': tx['from'],
        'value': tx['value'],
        'data': tx['input'],
    }

    # replay the transaction locally:
    try:
        w3.eth.call(replay_tx, tx.blockNumber - 1)
        print(f"{random_node_1} sent {amount} ETH to {random_node_2}")
        successful_transactions += 1
    except Exception as e:
        message = e.args[0]['message']
        print(message[message.find("revert ")+7:])

    if (i+1) % 100 == 0:
        num_successful_transactions.append(successful_transactions)
        successful_transactions = 0


########################################################################################################################################################

# DISPLAY THE RESULTS

print(f"The number of successful transactions per 100 transactions: {successful_transactions}")
print(f"Average number of successful transactions: {sum(num_successful_transactions)/len(num_successful_transactions)}")
print(f"Total number of successful transactions: {sum(num_successful_transactions)}")
print(f"Total number of failed transactions: {NUM_TRANSACTIONS - sum(num_successful_transactions)}")
print(f"Total number of transactions: {NUM_TRANSACTIONS}")
