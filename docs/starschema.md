# DIM_DATE

| Type     | Variable       | Description                                     | Source                                               |
| :------- | :------------- | :---------------------------------------------- | :--------------------------------------------------- |
| int      | `date_key`     | **PK** (Format: YYYYMMDD)                       | Auto-generated from Polygon `"t"` (timestamp) field. |
| datetime | `full_date`    | Actual trading date                             | Extracted from Polygon `"t"` (timestamp) field.      |
| int      | `day`          | Day of the month                                | Derived from `full_date`                             |
| int      | `month`        | Month                                           | Derived from `full_date`                             |
| int      | `year`         | Year                                            | Derived from `full_date`                             |
| int      | `quarter`      | Quarter of the year                             | Derived from `full_date`                             |
| varchar  | `day_of_week`  | Name of the day of the week                     | Derived from `full_date`                             |
| int      | `week_of_year` | Week number of the year                         | Derived from `full_date`                             |
| boolean  | `is_weekend`   | Flag indicating if the date is a weekend        | Derived from `full_date`                             |
| boolean  | `is_holiday`   | Flag indicating if the date is a public holiday | Derived from `full_date`                             |

# DIM_COMPANY

| Type    | Variable              | Description                                       | Source              |
| :------ | :-------------------- | :------------------------------------------------ | :------------------ |
| int     | `company_key`         | **PK** (Auto-increment)                           | System-generated    |
| varchar | `company_ticker`      | Stock ticker symbol traded on the exchange        | `companies.parquet` |
| varchar | `company_name`        | Full official name of the company                 | `companies.parquet` |
| varchar | `company_cik`         | Central Index Key used by the US SEC              | `companies.parquet` |
| boolean | `company_is_delisted` | Delisting status flag (True/False)                | `companies.parquet` |
| varchar | `company_location`    | Geographic location of the corporate headquarters | `companies.parquet` |

# DIM_INDUSTRY

| Type    | Variable           | Description                                            | Source                  |
| :------ | :----------------- | :----------------------------------------------------- | :---------------------- |
| int     | `industry_key`     | **PK** (Auto-increment)                                | System-generated        |
| varchar | `industry_sector`  | Major economic sector group                            | `industries.parquet`    |
| varchar | `industry_name`    | Specific business industry classification              | `industries.parquet`    |
| varchar | `company_category` | Market capitalization scale or category classification | `companies.parquet`     |
| varchar | `sic_industry`     | Standard Industrial Classification (SIC) code          | `sicindustries.parquet` |
| varchar | `sic_sector`       | Industry group description based on the SIC code       | `sicindustries.parquet` |

# DIM_EXCHANGE

| Type    | Variable             | Description                      | Source              |
| :------ | :------------------- | :------------------------------- | :------------------ |
| int     | `exchange_key`       | **PK** (Auto-increment)          | System-generated    |
| varchar | `exchange_name`      | Name of the stock exchange       | `exchanges.parquet` |
| varchar | `region_name`        | Geographic market region         | `regions.parquet`   |
| varchar | `region_market_type` | Market classification type       | `regions.parquet`   |
| time    | `region_local_open`  | Market opening time (Local Time) | `regions.parquet`   |
| time    | `region_local_close` | Market closing time (Local Time) | `regions.parquet`   |

---

# FACT_STOCK_DAILY

| Type    | Variable       | Description                                                            | Source / Logic                                |
| :------ | :------------- | :--------------------------------------------------------------------- | :-------------------------------------------- |
| int     | `date_key`     | **FK**                                                                 | Joins with `DIM_DATE`                         |
| int     | `company_key`  | **FK**                                                                 | Joins with `DIM_COMPANY`                      |
| int     | `industry_key` | **FK**                                                                 | Joins with `DIM_INDUSTRY`                     |
| int     | `exchange_key` | **FK**                                                                 | Joins with `DIM_EXCHANGE`                     |
| decimal | `open_price`   | Opening stock price for the day                                        | `ohlcs.parquet`                               |
| decimal | `high_price`   | Highest trading price recorded during the day                          | `ohlcs.parquet`                               |
| decimal | `low_price`    | Lowest trading price recorded during the day                           | `ohlcs.parquet`                               |
| decimal | `close_price`  | Closing stock price at the end of the session                          | `ohlcs.parquet`                               |
| bigint  | `volume`       | Total volume of shares traded                                          | `ohlcs.parquet`                               |
| decimal | `price_change` | Daily price variance                                                   | `close_price` - `open_price`                  |
| varchar | `price_trend`  | Categorized price direction status: `"up"`, `"down"`, or `"unchanged"` | Calculated conditionally using `price_change` |
