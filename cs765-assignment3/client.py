import json
import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from web3 import Web3

# CONSTANTS
GAS_AMOUNT = 30000000
NUM_NODES = 100
NUM_TRANSACTIONS = 1000
MEAN_VALUE = 5
m = 2
amount = 1

#connect to the local ethereum blockchain
provider = Web3.HTTPProvider('http://127.0.0.1:8545')
w3 = Web3(provider)
w3.eth.handleRevert = True
#check if ethereum is connected
print(w3.is_connected())

#replace the address with your contract address (!very important)
deployed_contract_address = '0x8EB25479eDE273613a31EA84A8B17E6eE7ee4968'

#path of the contract json file. edit it with your contract json file
compiled_contract_path ="build/contracts/DAPP.json"
with open(compiled_contract_path) as file:
    contract_json = json.load(file)
    contract_abi = contract_json['abi']
contract = w3.eth.contract(address = deployed_contract_address, abi = contract_abi)

########################################################################################################################################################

# CREATE THE NETWORK

G = nx.powerlaw_cluster_graph(NUM_NODES,m,0.5)
while not nx.is_connected(G):
    G = nx.powerlaw_cluster_graph(NUM_NODES,m,0.5)

weights = {edge: max(int(np.random.exponential(scale=MEAN_VALUE)),1) for edge in G.edges}
nx.set_edge_attributes(G, values=weights, name='weight')

def display_graph(G):
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'))
    nx.draw_networkx_labels(G, pos)
    plt.show()

display_graph(G)

########################################################################################################################################################

for i in range(NUM_NODES):
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

for edge in G.edges:
    txn_receipt = contract.functions.createAcc(edge[0], edge[1], G.edges[edge]['weight']).transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':GAS_AMOUNT})
    
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
        print(f"Account created between {edge[0]} and {edge[1]} with combined balance {2* G.edges[edge]['weight']}")
    except Exception as e:
        message = e.args[0]['message']
        print(message[message.find("revert ")+7:])

num_successful_transactions = []
successful_transactions = 0

for i in range(NUM_TRANSACTIONS):
    random_node_1 = random.randint(0,int(NUM_NODES/2))
    random_node_2 = random.randint(int(NUM_NODES/2)+1,NUM_NODES-1)
    while (random_node_1 == random_node_2):
        random_node_2 = random.randint(0,NUM_NODES-1)
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

    if (i+1) % NUM_NODES == 0:
        num_successful_transactions.append(successful_transactions)
        successful_transactions = 0

print(num_successful_transactions)
