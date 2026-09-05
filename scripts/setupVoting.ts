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

  console.log("\nAdding Student Council President candidates...");

  await (await voting.addCandidate(1, "Krishnamraju")).wait();
  await (await voting.addCandidate(1, "Karthik")).wait();
  await (await voting.addCandidate(1, "Avinash")).wait();

  console.log("President candidates added.");

  console.log("\nAdding Sports Secretary candidates...");

  await (await voting.addCandidate(2, "Yeswanth")).wait();
  await (await voting.addCandidate(2, "Harish")).wait();
  await (await voting.addCandidate(2, "Sai Babu")).wait();

  console.log("Sports candidates added.");

  console.log("\nAdding Academic Secretary candidates...");

  await (await voting.addCandidate(3, "Vinay")).wait();
  await (await voting.addCandidate(3, "Teja")).wait();
  await (await voting.addCandidate(3, "Parmesh")).wait();

  console.log("Academic candidates added.");

  console.log("\nAll 9 candidates added successfully.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
