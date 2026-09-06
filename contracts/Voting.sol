// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Voting {

    struct Candidate {
        uint256 id;
        string name;
        string symbol;
        uint256 voteCount;
    }

    struct Election {
        string name;
        bool started;
        bool ended;
        uint256 candidateCount;
        mapping(uint256 => Candidate) candidates;

        // Stores whether a student has voted in this election.
        // The key is the hash of the student's registration number.
        mapping(bytes32 => bool) hasVoted;
    }

    address public owner;

    uint256 public constant ELECTION_COUNT = 3;

    mapping(uint256 => Election) private elections;

    event CandidateAdded(
        uint256 electionId,
        uint256 candidateId,
        string name,
        string symbol
    );

    event VotingStarted(uint256 electionId);

    event VotingEnded(uint256 electionId);

    event VoteCast(
        uint256 electionId,
        bytes32 voterId,
        uint256 candidateId
    );

    constructor() {
        owner = msg.sender;

        elections[1].name = "Student Council President";
        elections[2].name = "Sports Secretary";
        elections[3].name = "Academic Secretary";
    }

    modifier onlyOwner() {
        require(
            msg.sender == owner,
            "Only owner can perform this action"
        );
        _;
    }

    modifier validElection(uint256 _electionId) {
        require(
            _electionId >= 1 &&
            _electionId <= ELECTION_COUNT,
            "Invalid election"
        );
        _;
    }

    modifier votingIsActive(uint256 _electionId) {
        require(
            elections[_electionId].started,
            "Voting has not started"
        );

        require(
            !elections[_electionId].ended,
            "Voting has ended"
        );

        _;
    }

    function addCandidate(
        uint256 _electionId,
        string memory _name,
        string memory _symbol
    )
        public
        onlyOwner
        validElection(_electionId)
    {
        require(
            !elections[_electionId].started,
            "Cannot add candidate after voting starts"
        );

        require(
            bytes(_name).length > 0,
            "Candidate name cannot be empty"
        );

        require(
            bytes(_symbol).length > 0,
            "Candidate symbol cannot be empty"
        );

        elections[_electionId].candidateCount++;

        uint256 candidateId =
            elections[_electionId].candidateCount;

        elections[_electionId].candidates[candidateId] =
            Candidate(
                candidateId,
                _name,
                _symbol,
                0
            );

        emit CandidateAdded(
            _electionId,
            candidateId,
            _name,
            _symbol
        );
    }

    function startVoting(uint256 _electionId)
        public
        onlyOwner
        validElection(_electionId)
    {
        require(
            elections[_electionId].candidateCount > 0,
            "Add candidates first"
        );

        require(
            !elections[_electionId].started,
            "Voting already started"
        );

        elections[_electionId].started = true;

        emit VotingStarted(_electionId);
    }

    /*
     * VOTE
     *
     * The student's registration number is converted
     * into a bytes32 hash by the backend.
     *
     * This allows:
     * - No MetaMask
     * - One vote per student per election
     * - Different students can vote
     */
    function vote(
        uint256 _electionId,
        uint256 _candidateId,
        bytes32 _voterId
    )
        public
        validElection(_electionId)
        votingIsActive(_electionId)
    {
        require(
            _voterId != bytes32(0),
            "Invalid voter ID"
        );

        require(
            !elections[_electionId].hasVoted[_voterId],
            "You have already voted in this election"
        );

        require(
            _candidateId > 0 &&
            _candidateId <=
            elections[_electionId].candidateCount,
            "Invalid candidate"
        );

        elections[_electionId]
            .hasVoted[_voterId] = true;

        elections[_electionId]
            .candidates[_candidateId]
            .voteCount++;

        emit VoteCast(
            _electionId,
            _voterId,
            _candidateId
        );
    }

    function endVoting(uint256 _electionId)
        public
        onlyOwner
        validElection(_electionId)
    {
        require(
            elections[_electionId].started,
            "Voting has not started"
        );

        require(
            !elections[_electionId].ended,
            "Voting already ended"
        );

        elections[_electionId].ended = true;

        emit VotingEnded(_electionId);
    }

    function restartVoting(uint256 _electionId)
        public
        onlyOwner
        validElection(_electionId)
    {
        require(
            elections[_electionId].started,
            "Voting has not started"
        );

        require(
            elections[_electionId].ended,
            "Voting is still active"
        );

        elections[_electionId].ended = false;

        emit VotingStarted(_electionId);
    }

    function getElectionName(uint256 _electionId)
        public
        view
        validElection(_electionId)
        returns (string memory)
    {
        return elections[_electionId].name;
    }

    function isVotingStarted(uint256 _electionId)
        public
        view
        validElection(_electionId)
        returns (bool)
    {
        return elections[_electionId].started;
    }

    function isVotingEnded(uint256 _electionId)
        public
        view
        validElection(_electionId)
        returns (bool)
    {
        return elections[_electionId].ended;
    }

    function getCandidate(
        uint256 _electionId,
        uint256 _candidateId
    )
        public
        view
        validElection(_electionId)
        returns (
            uint256 id,
            string memory name,
            string memory symbol,
            uint256 voteCount
        )
    {
        require(
            _candidateId > 0 &&
            _candidateId <=
            elections[_electionId].candidateCount,
            "Invalid candidate"
        );

        Candidate memory candidate =
            elections[_electionId]
                .candidates[_candidateId];

        return (
            candidate.id,
            candidate.name,
            candidate.symbol,
            candidate.voteCount
        );
    }

    function getAllCandidates(uint256 _electionId)
        public
        view
        validElection(_electionId)
        returns (Candidate[] memory)
    {
        uint256 count =
            elections[_electionId]
                .candidateCount;

        Candidate[] memory allCandidates =
            new Candidate[](count);

        for (
            uint256 i = 1;
            i <= count;
            i++
        ) {
            allCandidates[i - 1] =
                elections[_electionId]
                    .candidates[i];
        }

        return allCandidates;
    }

    /*
     * Check whether a student has voted.
     *
     * The backend sends the hashed registration number.
     */
    function hasVoted(
        uint256 _electionId,
        bytes32 _voterId
    )
        public
        view
        validElection(_electionId)
        returns (bool)
    {
        return elections[_electionId]
            .hasVoted[_voterId];
    }

    function getCandidateCount(uint256 _electionId)
        public
        view
        validElection(_electionId)
        returns (uint256)
    {
        return elections[_electionId]
            .candidateCount;
    }
}