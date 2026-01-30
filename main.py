import numpy as np
import pandas as pd

def main():
    
    df = pd.read_csv('RRP.csv', index_col=0)

    print(df)
    print(df['C01']['C00'])
    print(df.shape)


if __name__ == "__main__":
    main()
