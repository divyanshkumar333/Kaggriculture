# Kaggle Submission Checklist

## 1. Champion Profile
* **Champion**: `V018-B` (Batch Cap)
* **Champion Benchmark Score**: ~$51.4k mean (verified over 120 games)
* **Why V018-F was rejected**: V018-F did not demonstrate a statistically significant improvement over V018-B in the large-scale benchmark. V018-B won more head-to-head matchups, and when they tied, they were byte-for-byte identical. V018-B remains the proven and robust leader.

## 2. Exact File to Upload
* **File to Submit**: `main.py` (located in the repository root)
* **Status**: Cleanly copied from `agents/v018_b_batch_cap.py`. 100% functionally identical to the champion.

## 3. Pre-Submission Verifications
* **Algorithmic Integrity**: Frozen. No experimental code was removed to ensure zero behavioral deviation.
* **Dependencies**: Verified. Only Kaggle-native standard libraries (`math`, `os`, `json`, `collections`, `numpy`, `scipy.optimize`) and the competition's `kaggle_environments` are imported.
* **No File I/O**: Verified. The experimental metric tracker operates entirely in-memory and will gracefully collect into the `"unknown"` seed key on Kaggle without crashing or requiring disk access.
* **Local Tests**: `main.py` successfully completed simulated full-length (720-step) episodes against both `random` and `starter` agents.
* **Regression Suite**: Completed. (Known pre-existing `lux_ai_s3` import errors from the environment library remain, but do not impact the agent).

## 4. Required Kaggle Settings
There are no special settings required beyond ensuring you have joined the competition and accepted the rules. The `main.py` file is fully self-contained.

## 5. Final Manual Submission Steps

Follow these exact steps to submit the agent to Kaggle:

1. **Verify Kaggle Account**: Ensure you are logged into Kaggle in your terminal (using `~/.kaggle/kaggle.json` or `~/.kaggle/access_token` depending on your setup).
2. **Submit via CLI**: Run the following command from the root of this repository:
   ```bash
   kaggle competitions submit kaggriculture -f main.py -m "V018-B Batch Cap Champion"
   ```
3. **Monitor the Submission**: 
   ```bash
   kaggle competitions submissions kaggriculture
   ```
   Or view the validation status directly on the [Kaggriculture Leaderboard / My Submissions tab](https://www.kaggle.com/competitions/kaggriculture).
