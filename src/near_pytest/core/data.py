data = {
    "final_execution_status": "EXECUTED_OPTIMISTIC",
    "receipts_outcome": [
        {
            "block_hash": "Eb4FVHStxxwV9EzPSHTjmpCsfXk1nHPKAJs1xJvci3FW",
            "id": "CDqCjP3dtyxXrvJGaHuuLQb3zayjhBRFzgJtsZizp6Cn",
            "outcome": {
                "executor_id": "counter-4fd14aca.test.near",
                "gas_burnt": 4174947687500,
                "logs": [],
                "metadata": {"gas_profile": [], "version": 3},
                "receipt_ids": ["7jm6Mfo4CeHVP1qweSrSxqxwQizmAj2SMgaAXZxH31wp"],
                "status": {"SuccessValue": ""},
                "tokens_burnt": "417494768750000000000",
            },
            "proof": [],
        }
    ],
    "status": {"SuccessValue": ""},
    "transaction": {
        "actions": [
            "CreateAccount",
            {
                "AddKey": {
                    "access_key": {"nonce": 0, "permission": "FullAccess"},
                    "public_key": "ed25519:5hwHbM1e7r8gxb4emnywdSCkJmor3rnxGkFAr4YjKny5",
                }
            },
            {"Transfer": {"deposit": "10000000000000000000000000"}},
        ],
        "hash": "G83yVZmRo9PvwGv5XyNAQRC9biKZ5Psb5VnsNKemsSEe",
        "nonce": 1,
        "priority_fee": 0,
        "public_key": "ed25519:9snA3Sp2VCiUHJwxQ4fREtaBwT5PJZLyv4YSMsPESEcW",
        "receiver_id": "counter-4fd14aca.test.near",
        "signature": "ed25519:396WdxCQW7PCi3TscZ5VciAmv6fpGibXHJvhgUdvd2SyLAY33q8btPYCV55QtxswAJrkDCN3EFd4VJmhcpwtTDvM",
        "signer_id": "test.near",
    },
    "transaction_outcome": {
        "block_hash": "Bpsjh1yUqC5512XftAsnStgRQFmFzWEcuY4TwBYtRZqg",
        "id": "G83yVZmRo9PvwGv5XyNAQRC9biKZ5Psb5VnsNKemsSEe",
        "outcome": {
            "executor_id": "test.near",
            "gas_burnt": 4174947687500,
            "logs": [],
            "metadata": {"gas_profile": None, "version": 1},
            "receipt_ids": ["CDqCjP3dtyxXrvJGaHuuLQb3zayjhBRFzgJtsZizp6Cn"],
            "status": {
                "SuccessReceiptId": "CDqCjP3dtyxXrvJGaHuuLQb3zayjhBRFzgJtsZizp6Cn"
            },
            "tokens_burnt": "417494768750000000000",
        },
        "proof": [],
    },
}
