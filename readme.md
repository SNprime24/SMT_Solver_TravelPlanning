# SMT_SOLVER_TRAVELPLANNING


## Setup Environment

Create a conda environment and install dependency:
```bash
conda create -n fmtravelplanner python=3.9
conda activate fmtravelplanner
pip install -r requirements.txt
```

To run satisfiable plan generation experiment, refer to paper "TravelPlanner: A Benchmark for Real-World Planning with Language Agents" and their github repo to download their database and train/validation/test set.

## Running
#### Satisfiable Plan Solving 
The file for satisfiable plan generation experiment is
 `test_travelplanner.py`. 
An example command is 
```bash
python test_travelplanner.py  --set_type train --model_name gpt
```
*Note: You might want to use the training set to adjust the prompts for different LLMs. You can add customized checker for steps and codes to further improve the performance.*


## Evaluation
For satisfiable plan solving, after running experiments for a dataset (train/ validation/ test), 

run `convert_json.py` to convert the generated plan txt file to json files, and then run `collect_plans.py` to collect all plans to form a single jsonl file.

 Then, you can use this jsonl file and follow TravelPlanner's evaluation method to evaluate (either through [leaderboard](https://huggingface.co/spaces/osunlp/TravelPlannerLeaderboard) or through `eval.py` in TravelPlanner codebase)


## Prompts
The prompts we used are included in the `prompts` folder

## Citation
```md
@article{hao2024large,
  title={Large Language Models Can Solve Real-World Planning Rigorously with Formal Verification Tools},
  author={Hao, Yilun and Chen, Yongchao and Zhang, Yang and Fan, Chuchu},
  journal={arXiv preprint arXiv:2404.11891},
  year={2024}
}
```