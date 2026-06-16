## Data Availability

This repository contains:
- ✅ Synthesis pipeline code (`clause_generator/`)
- ✅ Inference code
- ✅ Evaluation prompts
- ✅ Dummy data samples (`dataset/generated/BL/dummy_*.json`, `dataset/generated/IV/dummy_*.json`)

This repository does NOT contain:
- ❌ Re-processed AI Hub source documents (per AI Hub redistribution policy)
- ❌ The full 15,082-specification corpus

To reproduce the full corpus:
1. Apply for access to AI Hub Dataset No. 71301 at https://aihub.or.kr
2. Run the VLM extraction step 
3. Run the synthesis pipeline
