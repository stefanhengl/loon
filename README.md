# # Hash Code 2015 - Loon

## Challenge 
[Click here](https://hashcode.withgoogle.com/past_editions.html) or check the downloaded assets in folder ./input.

## Strategy:
- Assign balloons to target rows proportionally to the number of targets in that row
- Balloons optimize their path to ...
    - minimize distance to their target row
    - maximize speed over the oceans, minimize speed over densly populated areas
    - avoid paths that might cause the balloon the get lost
- Start balloons randomly, but do not start two balloons with the same target row at the same time

## Performance:
The maximum achievable score is upper bounded by full-coverage for every move.
With 1050 targets and 400 time steps, the upper bound is 420.000 points. The code uses randomness to assign balloons to target rows and to decide whether to start a balloon. Hence, the results are 
non-deterministic. That being said, the code achieves scores around 380.000 points, which corresponds to **90% coverage**.

## Output:
Each simulation generates an output file *.out in ./output
with the score of the simulation as its filename.