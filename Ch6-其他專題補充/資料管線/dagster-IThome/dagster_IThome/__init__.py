from dagster import (
    AssetSelection,
    Definitions, 
    ScheduleDefinition,
    define_asset_job,
    load_assets_from_modules
)


from . import assets

all_assets = load_assets_from_modules([assets])

# 定義一個用來執行所有資產的工作
views_job = define_asset_job("IThome_views_job", selection=AssetSelection.all())

# 定義一個排程，每天晚上 9 點執行一次
views_schedule = ScheduleDefinition(
    name="IThome_views_schedule",
    cron_schedule="0 21 * * *",
    job=views_job,
)
    

defs = Definitions(
    assets=all_assets,
    schedules=[views_schedule],
)