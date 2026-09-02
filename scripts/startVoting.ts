import { network } from "hardhat";

async function main() {
  const { ethers } = await network.create();

  const [owner] = await ethers.getSigners();

  console.log("Using account:", owner.address);

  const voting = await ethers.getContractAt(
    "Voting",
    "0x9A9141aA574561eb6E0121a42E247D0b5e2A2f4d",
    owner
  );

  console.log("\nStarting Student Council President...");
  await (await voting.startVoting(1)).wait();
  console.log("President voting started.");

  console.log("\nStarting Sports Secretary...");
  await (await voting.startVoting(2)).wait();
  console.log("Sports voting started.");

  console.log("\nStarting Academic Secretary...");
  await (await voting.startVoting(3)).wait();
  console.log("Academic voting started.");

  console.log("\nAll 3 elections started successfully.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});