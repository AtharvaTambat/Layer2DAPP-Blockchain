// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DAPP{
    
    struct User {
        uint id;
        string name;
        uint balance;
        uint[] partners;
        uint partnerCount;
        bool exists;
    }
    
    struct Account {
        uint account_id;
        uint user1;
        uint user2;
        uint balance;
        uint[] contributions;
        bool exists;
    }
    
    mapping(uint => User) public users;
    uint public usersCount;
    mapping(uint => Account) public accounts;
    uint public accountsCount;
    
    function registerUser(uint id, string memory name) public {
        require(!users[id].exists, "User already exists");
        usersCount++;
        uint[] memory partners = new uint[](0);
        users[id] = User(id, name,0, partners, 0, true);
    }

    function getAccountId(uint user1, uint user2) public pure returns (uint) {
        uint smallerUserId = user1 < user2 ? user1 : user2;
        uint largerUserId = user1 < user2 ? user2 : user1;
        return uint(keccak256(abi.encodePacked(smallerUserId, largerUserId)));
    }
    
    // balance - is the balance of individual node
    function createAcc(uint user1, uint user2, uint balance) public {
        // users should exist
        require(users[user1].exists, "User 1 does not exist");
        require(users[user2].exists, "User 2 does not exist");

        // Account should not be created with the same user
        require(user1 != user2, "Cannot create account with same user");
        
        // Same account should not exist
        uint account_id = getAccountId(user1, user2);
        require(!accounts[account_id].exists, "Joint account already exists.");
        
        // Increment the accounts count
        accountsCount++;

        uint[] memory contributions = new uint[](2);
        contributions[0] = balance;
        contributions[1] = balance;

        // Updating the state of the users
        accounts[account_id] = Account(account_id, user1, user2, balance*2, contributions, true);
        users[user1].partners.push(user2);
        users[user2].partners.push(user1);
        users[user1].partnerCount++;
        users[user2].partnerCount++;
        users[user1].balance += balance;
        users[user2].balance += balance;
    }

    function sendAmount(uint user1,uint user2,uint amount) public{
        require(users[user1].exists, "User 1 does not exists");
        require(users[user2].exists, "User 2 does not exists");
        
        require(user1!=user2, "User cannot send money to self");
        
        bool[] memory visited = new bool[](usersCount);
        for (uint i = 0; i < visited.length; i++) {
            visited[i] = false; // set all elements to 10
        }

        uint currnode = user1;

        // Queue for BFS 
        uint[] memory queue = new uint[](usersCount);
        uint[] memory parent = new uint[](usersCount);
        // initializing the parent of each node as 2^256 -1 
        for(uint i = 0;i<usersCount;i++){
            parent[i] = type(uint).max;
        }
        uint front = 0;
        uint rear = 0;

        visited[user1] = true;
        queue[rear++] = user1;

        while(front != rear){
            currnode = queue[front++];
            if (currnode == user2){
                break;
            }
            
            for(uint adjacent = 0; adjacent < users[currnode].partnerCount;adjacent++){
                uint account_id = getAccountId(currnode, users[currnode].partners[adjacent]);
                uint currnode_contri = (currnode < users[currnode].partners[adjacent])? accounts[account_id].contributions[0] : accounts[account_id].contributions[1];

                // add it to BFS if it has not been visited and the edge (on source side) has suffecient balance
                if(!visited[users[currnode].partners[adjacent]] && currnode_contri >= amount){
                    parent[users[currnode].partners[adjacent]] = currnode;
                    visited[users[currnode].partners[adjacent]] = true;
                    queue[rear++] = users[currnode].partners[adjacent];
                }
            }
        }    

        // no path to user2 has enough amount
        require(currnode == user2, "No path with sufficient amount exists");
        if(currnode == user2){
            while(currnode!= user1){
                uint account_id = getAccountId(currnode, parent[currnode]);
                uint currnode_index = (currnode < parent[currnode])? 0:1;

                accounts[account_id].contributions[currnode_index] += amount;
                accounts[account_id].contributions[1-currnode_index] -= amount;

                users[currnode].balance += amount;
                users[parent[currnode]].balance -= amount;

                currnode = parent[currnode];
            }
        }  
    }
    
    function closeAccount(uint user1, uint user2) public {
        uint account_id = getAccountId(user1, user2);
        require(accounts[account_id].exists, "Account does not exist");

        // user1 changed to the lower user_id of the two
        uint smallerUserId = user1 < user2 ? user1 : user2;
        uint largerUserId = user1 < user2 ? user2 : user1;
        user1 = smallerUserId;
        user2 = largerUserId;

        users[user1].balance += accounts[account_id].contributions[0];
        users[user2].balance += accounts[account_id].contributions[1];
        
        for (uint i = 0; i < users[user1].partnerCount; i++) {
            if (users[user1].partners[i] == user2) {
                users[user1].partners[i] = users[user1].partners[users[user1].partnerCount - 1];
                users[user1].partnerCount--;
                break;
            }
        }

        users[user1].partners.pop();
        
        for (uint i = 0; i < users[user2].partnerCount; i++) {
            if (users[user2].partners[i] == user1) {
                users[user2].partners[i] = users[user2].partners[users[user2].partnerCount - 1];
                users[user2].partnerCount--;
                break;
            }
        }

        users[user2].partners.pop();
        
        delete accounts[account_id];

        accountsCount--;
    }
}