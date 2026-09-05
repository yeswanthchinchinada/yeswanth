import { network } from "hardhat";

async function main() {
const { ethers } = await network.create();

const voting = await ethers.deployContract("Voting");

await voting.waitForDeployment();

const votingAddress = await voting.getAddress();

console.log("Voting contract deployed to:", votingAddress);

console.log("Adding candidates automatically...");

// Student Council President
await (await voting.addCandidate(1, "Krishnamraju", "🥛")).wait();
await (await voting.addCandidate(1, "Karthik", "🚲")).wait();
await (await voting.addCandidate(1, "Avinash", "🪭")).wait();

// Sports Secretary
await (await voting.addCandidate(2, "Yeswanth", "📣")).wait();
await (await voting.addCandidate(2, "Harish", "⚽")).wait();
await (await voting.addCandidate(2, "Sai Babu", "🏏")).wait();

// Academic Secretary
await (await voting.addCandidate(3, "Vinay", "📋")).wait();
await (await voting.addCandidate(3, "Teja", "🖊️")).wait();
await (await voting.addCandidate(3, "Parmesh", "📖")).wait();

console.log("All candidates added successfully!");
}

main().catch((error) => {
console.error(error);
process.exitCode = 1;
});
