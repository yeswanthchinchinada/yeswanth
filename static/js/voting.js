const CONTRACT_ADDRESS = "0x9A9141aA574561eb6E0121a42E247D0b5e2A2f4d";

const CONTRACT_ABI = [
    "function vote(uint256 _electionId, uint256 _candidateId)",
    "function hasVoted(uint256 _electionId, address _voter) view returns (bool)",
    "function isVotingStarted(uint256 _electionId) view returns (bool)",
    "function isVotingEnded(uint256 _electionId) view returns (bool)"
];

let provider;
let signer;
let votingContract;
let walletAddress = null;


async function connectMetaMask() {

    if (typeof window.ethereum === "undefined") {

        alert(
            "MetaMask is not installed. Please install MetaMask."
        );

        return false;
    }

    try {

        provider =
            new ethers.BrowserProvider(
                window.ethereum
            );

        await provider.send(
            "eth_requestAccounts",
            []
        );


        /* AUTOMATICALLY SWITCH TO GANACHE */

        try {

            await window.ethereum.request({

                method:
                    "wallet_switchEthereumChain",

                params: [
                    {
                        chainId: "0x539"
                    }
                ]

            });

        }

        catch (switchError) {

            if (
                switchError.code === 4902 ||
                switchError.code === -32603
            ) {

                await window.ethereum.request({

                    method:
                        "wallet_addEthereumChain",

                    params: [
                        {
                            chainId: "0x539",

                            chainName:
                                "Ganache Local",

                            nativeCurrency: {
                                name:
                                    "Ethereum",

                                symbol:
                                    "ETH",

                                decimals: 18
                            },

                            rpcUrls: [
                                "http://127.0.0.1:7545"
                            ]
                        }
                    ]

                });

            }

            else {

                throw switchError;

            }

        }


        /* RECREATE PROVIDER AFTER NETWORK SWITCH */

        provider =
            new ethers.BrowserProvider(
                window.ethereum
            );

        signer =
            await provider.getSigner();

        walletAddress =
            await signer.getAddress();


        votingContract =
            new ethers.Contract(
                CONTRACT_ADDRESS,
                CONTRACT_ABI,
                signer
            );


        const network =
            await provider.getNetwork();


        if (network.chainId !== 1337n) {

            alert(
                "MetaMask is not connected to Ganache Local.\n\n" +
                "Current Chain ID: " +
                network.chainId.toString()
            );

            return false;
        }


        return true;

    }

    catch (error) {

        console.error(
            "MetaMask connection error:",
            error
        );


        if (error.code === 4001) {

            alert(
                "MetaMask connection was rejected."
            );

        }

        else {

            alert(
                "MetaMask connection failed.\n\n" +
                "Please make sure Ganache is running."
            );

        }


        return false;
    }
}



async function castVote(
    electionId,
    candidateId,
    candidateName
) {

    const connected =
        await connectMetaMask();


    if (!connected) {

        return false;

    }


    try {

        /* CHECK WHETHER USER ALREADY VOTED */

        const alreadyVoted =
            await votingContract.hasVoted(
                electionId,
                walletAddress
            );


        if (alreadyVoted) {

            alert(
                "You have already voted in this election."
            );

            return false;

        }


        /* CHECK VOTING STATUS */

        const started =
            await votingContract.isVotingStarted(
                electionId
            );


        const ended =
            await votingContract.isVotingEnded(
                electionId
            );


        if (!started) {

            alert(
                "Voting has not started yet."
            );

            return false;

        }


        if (ended) {

            alert(
                "Voting has ended."
            );

            return false;

        }


        /* CONFIRM VOTE */

        const confirmVote =
            confirm(
                "Confirm your vote for " +
                candidateName +
                "?"
            );


        if (!confirmVote) {

            return false;

        }


        /* SEND BLOCKCHAIN TRANSACTION */

        const transaction =
            await votingContract.vote(
                electionId,
                candidateId
            );


        alert(
            "MetaMask transaction submitted.\n\n" +
            "Please confirm the transaction in MetaMask."
        );


        /* WAIT FOR BLOCKCHAIN CONFIRMATION */

        await transaction.wait();


        /* SAVE VOTING HISTORY */

        try {

            await fetch(
                "/save-vote-history",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        election_id:
                            electionId,

                        candidate_id:
                            candidateId,

                        candidate_name:
                            candidateName,

                        transaction_hash:
                            transaction.hash
                    })
                }
            );

        }

        catch (historyError) {

            console.error(
                "Voting history error:",
                historyError
            );

        }


        /* SUCCESS NOTIFICATION */

        alert(
            "Vote successfully recorded on blockchain!\n\n" +
            "Candidate: " +
            candidateName +
            "\n\n" +
            "Transaction Hash:\n" +
            transaction.hash +
            "\n\n" +
            "Click OK to continue."
        );


        if (
            typeof showMessage === "function"
        ) {

            showMessage(
                "Vote recorded: " +
                candidateName
            );

        }


        return true;

    }

    catch (error) {

        console.error(
            "Voting error:",
            error
        );


        if (
            error.code === 4001 ||
            error.code === "ACTION_REJECTED"
        ) {

            alert(
                "Transaction rejected in MetaMask."
            );

        }

        else if (
            error.code === "INSUFFICIENT_FUNDS"
        ) {

            alert(
                "Insufficient ETH in the MetaMask account.\n\n" +
                "Please use a Ganache-funded account."
            );

        }

        else {

            alert(
                "Voting failed.\n\n" +
                "Error: " +
                (
                    error.shortMessage ||
                    error.message ||
                    "Unknown error"
                )
            );

        }


        return false;

    }

}