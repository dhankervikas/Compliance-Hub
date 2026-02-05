from app.services.data_adapter import DataSourceAdapter

adapter = DataSourceAdapter()
data = adapter.get_all_evidence()

print(f"Type of returned data: {type(data)}")
if isinstance(data, list):
    print(f"List length: {len(data)}")
    if len(data) > 0:
        print(f"First item type: {type(data[0])}")
else:
    print(f"Returned data keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
