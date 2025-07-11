import pandas as pd
import argparse

def process_data(data):
    data["ops"] = data["size"]**3*2
    data["bw_conf_eff"] = 16*data["rocc"]/(data["cycles"]*3)
    data["Ioc"] = data["ops"]/(data["rocc"]*16)
    data["p_attain_seq"] =  1 / ((1/512) + (1/(data["Ioc"]*data["bw_conf_eff"])))
    print(data)
    return data

def main():
    parser = argparse.ArgumentParser(description="Generate performance plots (roofline or bar).")
    parser.add_argument(
        '-i',
        '--input-path', 
        type=str, 
        help="Path to the pickle file or results folder."
    )
    parser.add_argument(
        '-o',
        '--output-path', 
        type=str, 
        help="Path to the output, also enables figure exporting"
    )

    args = parser.parse_args()
    data = pd.read_pickle(args.input_path)
    data = process_data(data)

if __name__ == "__main__":
    main()

