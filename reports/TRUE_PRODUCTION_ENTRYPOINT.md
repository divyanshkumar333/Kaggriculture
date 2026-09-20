# True Production Entrypoint Analysis

To definitively answer which agent represents our "Current Champion" and what is actually packaged for Kaggle, I ran an exact byte-size and SHA256 cryptographic hash analysis across the repository's root files and the `agents/` directory.

## 1. The Discrepancy
The previous repository documentation claimed `v051_v16_lookahead30_final.py` (23,562 bytes) was promoted as the final 2900+ Kaggle candidate. However, `main.py` is currently a 28,695 byte file labeled internally as "Agent V032: V031 + 4-Step Front-Running Lookahead". 

Meanwhile, `agents/v032_grandmaster.py` is only 18,857 bytes, proving that `main.py` is NOT a pure copy of V032 either.

## 2. Hash Evidence

| File | Byte Size | SHA256 Hash |
| :--- | :--- | :--- |
| `main.py` | 28,695 | 8a9b079d66836e0dbe1fc7630979a0a1f1d7624e366c40fb0e58a16945be903c |
| `agents/v032_grandmaster.py` | 18,857 | 0d76eed02414bbb05489a59ca86088669a778c39b06ba2a6dc05cfe976ad647e |
| `agents/v051_v16_lookahead30_final.py` | 23,562 | 5dc2ef2a460905c750ab0c072bfbb5e0d20d43fecd7a30b404d2cf397b1c4785 |

## 3. What is Actually Packaged
`main.py` is the file required by the Kaggle environments `tar.gz` submission bundle. Therefore, the **Actual Kaggle Submission** is `main.py` (28,695 bytes). 

By inspecting the source of `main.py`, I identified that it relies on a hardcoded trace replay array (`_ACTIONS = json.loads(zlib.decompress(base64.b85decode(...)))`). 
Its byte-size expansion corresponds to embedding a massive base64 string from a very long replay trace, heavily suggesting that it is a hardcoded trace execution agent rather than a dynamic policy.

## 4. Final Verdict
- **Production Candidate (Kaggle Submission)**: `main.py` (The 28,695 byte trace-replay variant of V032).
- **Historical Champion**: `agents/v051_v16_lookahead30_final.py` (Promoted in git commit history, but never actually deployed over `main.py`).
- **Best Locally Verified H2H Candidate**: `agents/v025_a_aggressive_cows.py` (Still the strongest empirical dynamic agent against a diverse meta).

> [!WARNING]
> `main.py` is stale executable code that does not reflect the latest V051 advancements. It is effectively a trace-replay clone frozen in time.
