# # Hash Code 2015 - Loon

## Challenge 
[Click here](https://hashcode.withgoogle.com/past_editions.html)

## Strategy:
- Calculate number of targets per row
- Introduce target rows: balloons will optimize their path to stay close to their target row
- Assign balloons to target row proportionally to the number of targets on that row
- Start balloons randomly, but do not start two balloons with the same target row at the same time
- (not yet implemented) Optimize speed: move fast over water and slow over densly populated areas

