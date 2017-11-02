# # Hash Code 2015 - Loon

## Challenge 
[Click here](https://hashcode.withgoogle.com/past_editions.html) or check the downloaded assets in folder ./input.

## Strategy:
- Balloons optimize their path to ...
    - minimize their distance to an assigned **target row**
    - maximize their speed over the oceans, minimize their speed over densly populated areas
    - avoid paths that might cause the balloon to get lost
- Balloons start as soon as their coverage does not overlap with the coverage of their direct predecessor with the same target row
- A greedy algorithm finds a list of target rows for the balloons: one balloon is added at a time and for this balloon the target row with the highest score is determined.

## Score:
The maximum achievable score is upper bounded by full-coverage for every move.
With 1050 targets and 400 time steps, the upper bound is 420.000 points. The code achieves a score of 225.992 points, which corresponds to **54% coverage**.

## Output:
Each simulation generates an output file *.out in ./output with the score of the simulation as its filename.
