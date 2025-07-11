from accfg_artifacts.plot_gemmini import process_data
from accfg_artifacts.plot_snax import change_option_labels
import pandas as pd
from scipy.stats import gmean
import argparse

def main(result_folder: str):
    print("Gemmini Data:")
    df = process_data(pd.read_pickle(result_folder + '/gemmini_results.pkl'))
    print(df)

    # Pivot to align values for the same size
    pivot = df.pivot(index="size", columns="option", values="p_attain_seq")

    # Calculate the ratio
    pivot['ratio'] = pivot["MLIR deduplicated"] / pivot["C baseline"]

    # Calculate geometric mean of the ratios
    geo_mean_increase = gmean(pivot['ratio'])
    print(f"Geometric mean increase of p_attain_seq (MLIR deduplicated over C baseline): {geo_mean_increase:.3f}x")

    print("==========")
    print("OpenGemm Data:")
    df = change_option_labels(pd.read_pickle(result_folder + '/opengemm_results.pkl'))
    print(df)
    # Pivot to align values for the same size
    # P_meas is measured performance
    pivot = df.pivot(index="size", columns="option", values="p_meas")

    # Calculate the ratio
    pivot['ratio'] = pivot["With Optimizations"] / pivot["Base (MLIR)"]

    # Calculate geometric mean of the ratios
    geo_mean_increase = gmean(pivot['ratio'])
    print(f"Geometric mean increase of P_measured (With Optimizations over Base (MLIR)): {geo_mean_increase:.3f}x")
    print(f"Peak increase of P_measured: {pivot['ratio'].max():.3f}x")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Show results of experiments")
    parser.add_argument(
        '-i',
        '--input-path', 
        type=str, 
        help="Path to the folder containing pickle files."
    )
    args = parser.parse_args()
    main(args.input_path)
    