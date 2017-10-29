# # Hash Code 2015 - Loon

## Challenge 
[Click here](https://hashcode.withgoogle.com/past_editions.html) or check the downloaded assets in folder `input`

## Strategy:
- Calculate number of targets per row
- Introduce target rows: balloons will optimize their path to stay close to their target row
- Assign balloons to target rows proportionally to the number of targets on that row
- Start balloons randomly, but do not start two balloons with the same target row at the same time
- Move fast over water and slow over densly populated areas

## Performance:
The maximum achievable score is upper bounded by full-coverage with every move.
With 1050 targets and 400 time steps, the upper bound is 420.000 points. The strategy uses randomness for assigning balloons to target rows and for deciding when to start a balloon. Hence, the results are 
non-deterministic. That being said, the code achieves scores around 380.000 points, which corresponds to **90% coverage**.

## Output:
Each simulation generates an output file *.out in ./output
with the score of the simulation as its filename.