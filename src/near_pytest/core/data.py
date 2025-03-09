data = {
    "final_execution_status": "EXECUTED_OPTIMISTIC",
    "receipts_outcome": [
        {
            "block_hash": "4UY8dn181RJ9Ss3xdhQL7Tnfs9CTRRRpUCeAijVt2pnL",
            "id": "9chwEbYorQQ5diXNjz16NoXPu3AjoLm7JoWz6QKpNndC",
            "outcome": {
                "executor_id": "counter-d1e90d08.test.near",
                "gas_burnt": 1567337341817,
                "logs": [],
                "metadata": {
                    "gas_profile": [
                        {
                            "cost": "BASE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "1853376777",
                        },
                        {
                            "cost": "CONTRACT_LOADING_BASE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "35445963",
                        },
                        {
                            "cost": "CONTRACT_LOADING_BYTES",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "396905329855",
                        },
                        {
                            "cost": "READ_CACHED_TRIE_NODE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "2280000000",
                        },
                        {
                            "cost": "READ_MEMORY_BASE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "10439452800",
                        },
                        {
                            "cost": "READ_MEMORY_BYTE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "155854653",
                        },
                        {
                            "cost": "READ_REGISTER_BASE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "5034330372",
                        },
                        {
                            "cost": "READ_REGISTER_BYTE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "197124",
                        },
                        {
                            "cost": "STORAGE_READ_BASE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "56356845749",
                        },
                        {
                            "cost": "STORAGE_READ_KEY_BYTE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "154762665",
                        },
                        {
                            "cost": "STORAGE_READ_VALUE_BYTE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "5611004",
                        },
                        {
                            "cost": "STORAGE_WRITE_BASE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "64196736000",
                        },
                        {
                            "cost": "STORAGE_WRITE_EVICTED_BYTE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "32117307",
                        },
                        {
                            "cost": "STORAGE_WRITE_KEY_BYTE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "352414335",
                        },
                        {
                            "cost": "STORAGE_WRITE_VALUE_BYTE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "31018539",
                        },
                        {
                            "cost": "TOUCHING_TRIE_NODE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "48305867778",
                        },
                        {
                            "cost": "WASM_INSTRUCTION",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "81762200256",
                        },
                        {
                            "cost": "WRITE_MEMORY_BASE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "5607589722",
                        },
                        {
                            "cost": "WRITE_MEMORY_BYTE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "5447544",
                        },
                        {
                            "cost": "WRITE_REGISTER_BASE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "5731044972",
                        },
                        {
                            "cost": "WRITE_REGISTER_BYTE",
                            "cost_category": "WASM_HOST_COST",
                            "gas_used": "7603128",
                        },
                    ],
                    "version": 3,
                },
                "receipt_ids": ["APmpfFaK2YwUEtJAxsgVHeZXoRNnTU7nbpzVZ5DrXtms"],
                "status": {"SuccessValue": "U2l4dHkgTmluZSBwZW9wbGUgaW4gdGhlIHdvcmxk"},
                "tokens_burnt": "156733734181700000000",
            },
            "proof": [
                {
                    "direction": "Left",
                    "hash": "9fu6ZvjpN7JwTFvwptoYc6oa4Bjgw3d73i9uBCtPYh5W",
                }
            ],
        }
    ],
    "status": {"SuccessValue": "U2l4dHkgTmluZSBwZW9wbGUgaW4gdGhlIHdvcmxk"},
    "transaction": {
        "actions": [
            {
                "FunctionCall": {
                    "args": "e30=",
                    "deposit": "0",
                    "gas": 200000000000000,
                    "method_name": "increment",
                }
            }
        ],
        "hash": "9w8sobZuCgvqtWKntNYdZ94xzXJcjsd5p8tkHdzHaLrc",
        "nonce": 5000004,
        "priority_fee": 0,
        "public_key": "ed25519:H8SEPfBc8JTNhen6886WEZxq7UPVTNKcemPZkHXtNMUe",
        "receiver_id": "counter-d1e90d08.test.near",
        "signature": "ed25519:28kP7EYmaEJJ14pZHKo8JDtQzJSyfv4SZYr73fKtP31FSc4XYpaQwuGB3eKFUWcPdkwoZuYewVSCCXfLURaqHp8x",
        "signer_id": "counter-d1e90d08.test.near",
    },
    "transaction_outcome": {
        "block_hash": "4UY8dn181RJ9Ss3xdhQL7Tnfs9CTRRRpUCeAijVt2pnL",
        "id": "9w8sobZuCgvqtWKntNYdZ94xzXJcjsd5p8tkHdzHaLrc",
        "outcome": {
            "executor_id": "counter-d1e90d08.test.near",
            "gas_burnt": 308084095274,
            "logs": [],
            "metadata": {"gas_profile": None, "version": 1},
            "receipt_ids": ["9chwEbYorQQ5diXNjz16NoXPu3AjoLm7JoWz6QKpNndC"],
            "status": {
                "SuccessReceiptId": "9chwEbYorQQ5diXNjz16NoXPu3AjoLm7JoWz6QKpNndC"
            },
            "tokens_burnt": "30808409527400000000",
        },
        "proof": [
            {
                "direction": "Right",
                "hash": "F7m4vUUEakugGdCKtVcsoQD8jqoA6ut3k9fR3VMbzsUf",
            }
        ],
    },
}
