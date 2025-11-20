from src.data_fetcher import iter_csv_records

#-----------------------Testing the CSV--------------------------------------------
# Tests to read the CSV rows with the iter_csv_records
def test_iter_csv_records_reads_rows(tmp_path):
    path = tmp_path / "demo.csv"
    path.write_text("A,B\n1, 2\n3,4\n", encoding="utf-8")
    rows = list(iter(iter_csv_records(path)))
    assert rows == [{"A": "1", "B": "2"}, {"A": "3", "B": "4"}]
    
def test_iter_csv_records_empty_okay(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("A,B\n", encoding="utf-8")
    assert list(iter_csv_records(path)) == []   