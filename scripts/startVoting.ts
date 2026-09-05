import { network } from "hardhat";

async function main() {
const { ethers } = await network.create();

const [owner] = await ethers.getSigners();

console.log("Using account:", owner.address);

const voting = await ethers.getContractAt(
"Voting",
"0x0539A968714bc20C2946e6dC9Ff88fbE2826e93e",
owner
);

console.log("\nChecking Student Council President...");
if (await voting.isVotingStarted(1)) {
console.log("President voting already started. Skipping.");
} else {
await (await voting.startVoting(1)).wait();
console.log("President voting started.");
}

console.log("\nChecking Sports Secretary...");
if (await voting.isVotingStarted(2)) {
console.log("Sports voting already started. Skipping.");
} else {
await (await voting.startVoting(2)).wait();
console.log("Sports voting started.");
}

console.log("\nChecking Academic Secretary...");
if (await voting.isVotingStarted(3)) {
console.log("Academic voting already started. Skipping.");
} else {
await (await voting.startVoting(3)).wait();
console.log("Academic voting started.");
}

console.log("\nAll elections checked successfully.");
}

main().catch((error) => {
console.error(error);
process.exitCode = 1;
});
