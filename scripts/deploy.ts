import { network } from "hardhat";

async function main() {
  const { ethers } = await network.create();

  const voting = await ethers.deployContract("Voting");

  await voting.waitForDeployment();

  console.log(
    "Voting contract deployed to:",
    await voting.getAddress()
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});