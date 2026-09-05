async function castVote(
    electionId,
    candidateId,
    candidateName
) {

    try {

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


        /* SEND VOTE TO FLASK BACKEND */

        const response =
            await fetch(
                "/submit-vote",
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
                            candidateName

                    })
                }
            );


        const result =
            await response.json();


        /* CHECK BACKEND RESPONSE */

        if (!result.success) {

            alert(
                result.message ||
                "Voting failed."
            );

            return false;

        }


        /* SUCCESS MESSAGE */

        alert(
            "Vote successfully recorded on blockchain!\n\n" +

            "Candidate: " +
            result.candidate_name +

            "\n\n" +

            "Transaction Hash:\n" +
            result.transaction_hash +

            "\n\n" +

            "Your vote has been securely stored on blockchain."
        );


        /* SHOW PAGE MESSAGE */

        if (
            typeof showMessage === "function"
        ) {

            showMessage(
                "Vote recorded: " +
                result.candidate_name
            );

        }


        return true;

    }

    catch (error) {

        console.error(
            "Voting error:",
            error
        );


        alert(
            "Voting failed.\n\n" +
            "Please make sure Ganache and Flask are running."
        );


        return false;

    }

}