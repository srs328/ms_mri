# Auto3dSeg

[YouTube tutorial](https://www.youtube.com/watch?v=wEfLVnL-7D4)

## Dice

- Dice Score is a measure of similarity between predicted segmentation and ground truth segmentation mask
- [Here](https://pycad.co/the-difference-between-dice-and-dice-loss/) is a good explanation of Dice score and Dice loss

## Cross Validation

[Tutorial](https://github.com/Project-MONAI/tutorials/blob/main/modules/cross_validation_models_ensemble.ipynb)

## The Training Work Directory

- `best_metric_model.pt` is the trained model, and each fold has one

## Ensemble Predictions

[Documentation](https://docs.monai.io/en/0.8.1/_modules/monai/handlers/segmentation_saver.html) about saving predictions (i.e. `pred = ensemble( pred_param={...} )`)

## Event File

### Notes on choroid_pineal_pituitary_T1-1

- Steps is (num epochs)*(some variable [12 in the case of choroid_pineal_pituitary])
  - Is that variable 2*val_files?
- Every 5 epochs it's computing the Dice (evaluation metric) for each class
