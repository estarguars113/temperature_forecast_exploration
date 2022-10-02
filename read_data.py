import pandas as pd
import xarray as xr

file='data/20201205_tmin_15days_forecast.nc' 

ds = xr.open_dataset(file)
df = ds.to_dataframe()

lyon_area_df = df[df.index.get_level_values('lat').isin([45.0, 46.0, 47.0])]
lyon_area_df = lyon_area_df[lyon_area_df.index.get_level_values('lon').isin([4.0, 5.0, 6.0])]
print(lyon_area_df)