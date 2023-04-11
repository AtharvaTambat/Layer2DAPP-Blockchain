var Payment = artifacts.require("DAPP.sol");

module.exports = function(deployer) {
  deployer.deploy(Payment);
};
