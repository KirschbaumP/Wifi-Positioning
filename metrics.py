from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np

def print_metrics(y_pred, y_true):
    mse_x = mean_squared_error(y_true.loc[:, 'position_x'], y_pred[:, 0])
    mse_y = mean_squared_error(y_true.loc[:, 'position_y'], y_pred[:, 1])
    rmse_x, rmse_y = np.sqrt(mse_x), np.sqrt(mse_y)

    mae_x = mean_absolute_error(y_true.loc[:, 'position_x'], y_pred[:, 0])
    mae_y = mean_absolute_error(y_true.loc[:, 'position_y'], y_pred[:, 1])

    # Euklidischer Fehler
    errors = np.linalg.norm((y_true - y_pred).astype(float), axis=1)
    mean_pos_error = np.mean(errors)
    median_pos_error = np.median(errors)

    print("RMSE:", mean_squared_error(y_true, y_pred))
    print("RMSE X:", rmse_x, "RMSE Y:", rmse_y)
    print("MAE X:", mae_x, "MAE Y:", mae_y)
    print("Mean Position Error:", mean_pos_error)
    print("Median Position Error:", median_pos_error)