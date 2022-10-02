# Temperature forecast exploration

The purpose of this project is to get an initial overview of the dataset provided and identify the best strategies to process, store and expose the information

## How to use

### Requirements

* Docker
* Data folder with the source files

### Why to use Docker

The base image selected for the project geopython/pygeoapi contains already all the dependencies to handle netcdf files with xarray library without the need to configure those in the host user environment
  
### Database modeling

Assuming that the goal is to allow queries defining specific sets of coordinates, or geographical references, like city or country name, but also supporting time-efficient filtering

#### Geospatial based queries

##### Requirements
 * Postgres
 * Postgis

The support database selected will be postgres in combination with the extension postgis, to support geographical data types, in this case specifically we would assume that the possible expected queries are the type of:
* Bring me all the temperature forecasts made for this city/coordinates window

To support that we would use 2 of the supported geometries by postgis:

* Point, to represent a specific point in space(lat, lon) enriched with the prediction data
* Polygon to represent reference places that can be used to filter

Query example: Return the minimum temperature expected in the Lyon's area
```sql
    WITH city AS (
        SELECT 'Lyon' AS name,
            ST_Buffer(ST_Point(4.0,45), 2) AS geom --order is (lon, lat)
    )
    , prediction(predicted_time, temp,geom) AS (
        VALUES
        ('2020-02-11', 240, ST_Point(0.1,0))
        , ('2020-02-12', 252, ST_Point(1,1) )
    )
    SELECT min(temp)
    FROM city INNER JOIN prediction
        ON ST_Contains(city.geom, prediction.geom)
    GROUP BY city.geom;
```

In the anterior example, Lyon's area was defined using a coordinates window, however given the level of detail expected we can define it explicitly via a poligon.

For reference places of common use, usually this polygon definition is available and can be imported directly into the database. [Here](https://github.com/iTowns/iTowns2-sample-data/blob/master/lyon-ZU.geojson) is a link for the Lyon polygon definition in geojson format, that can be imported into the databases using a command similar to this:

```sql
INSERT INTO city(name, geom)
    VALUES ('cit_name', 
    ST_TRANSFORM(ST_GeomFromGeoJSON('geojson_definition'));
```

The geojson format can be used in the data visualization. Libraries like plotly, mapbox are integrated with this format to draw maps, including the creation of heat maps using attribute values

##### More information
* [Postgis main page](https://postgis.net/)
* Postgis geometries supported: [http://postgis.net/workshops/postgis-intro/geometries.html](http://postgis.net/workshops/postgis-intro/geometries.html)


#### Time based queries

Let's assume initially that the expected granularity used in the queries is daily level, in such case, it would be better to use time-based partitions to improve the filtering and consequently the response time, this will imply convert our previous table defintion in the following way

Query example: Return the minimum temperature expected in the Lyon's area for the month of february in all the years
```sql
    WITH city AS (
        SELECT 'Lyon' AS name,
            ST_Buffer(ST_Point(4.0,45), 2) AS geom --order is (lon, lat)
    )
    -- year, month and day are partition fields
    , prediction(predicted_time, year, month, day, temp,geom) AS (
        VALUES
        ('2020-02-11', 2020, 2, 11, 240, ST_Point(0.1,0))
        , ('2020-02-12', 2020, 2, 12, 252, ST_Point(1,1) )
    )
    SELECT min(temp)
    FROM city INNER JOIN prediction
        ON ST_Contains(city.geom, prediction.geom)
    where month = 2
    GROUP BY city.geom;
```

It's reasonable to consider that the daily granularity is expected in a defined time window and that events far in the past are not usually queried by day but for specific periods of time.
We can create intermediate tables , with values previously aggregated for the most common requested queries
```sql
CREATE MATERIALIZED VIEW aggregated_month AS 
SELECT 
month, min(temp) as min_temp, max(temp) as max_temp, avg(temp) as avg_temp
FROM prediction
group by month;
```

### Storage modeling
The information can be also stored in a cloud-based storage like can be Azure blob storage and save the data in a columnar format parquet, following a partition definition like the previously defined. This format has some advantages that can be useful in the current context:
* Compress files by finding value similarities inside the column values
* Improving columnar operations like the ones exposed in the example of the materialized


# Pending things to do
* Expose jupyter notebook explores via browser in host pc
* Cover data load into the database using the processing script
* Strategy to fetch the input files directly from the source via API consumption
* In addition to the use of materialized views, it's possible to use a cache system like redis, which based on the analysis of commonly used queries, cache materialized views to respond faster
