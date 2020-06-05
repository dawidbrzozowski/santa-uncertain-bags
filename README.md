# Santa's uncertain bags. Kaggle competition. Project for ALHE.
Link to the competition: https://www.kaggle.com/c/santas-uncertain-bags
### Get all packages needed in project using pip install -r requirements.txt

## The application has many ways to run. Available arguments:
\-- max_bag_weight - max bag weight (capacity), that will be used during packing bags algorithm. <br>
\-- std_mul - how much impact standard deviation should have on packaging <br>
\-- step_mul - Default step used in 1+1 algorithm for making random step. Default value = 0.6 <br>
\-- save_path - path to save your bags, calculated for algorithm. <br>
\-- find_weights - launches 1+1 algorithm for searching better gift weights. Saves calculated weights to data/temp_weights.json <br>
    If you want to get the output for newly created weights, change default weights and then run the algorithm. <br>
    
## Example usages:
Run from the main directory: <br>
python -m solvers.bag_packing --save_path data/output.csv --max_bag_weight 42 --std_mul 0.4
This would return the score and also save the output ready for kaggle evaluation.
<br>
python -m solvers.baseline --find_weights --max_bag_weight 50 --std_mul 0.6
This would run the 1+1 algorithm and save calculated weights to data/temp_weights.json
