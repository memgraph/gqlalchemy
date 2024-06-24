def test_get_transactions(memgraph):
    result = memgraph.get_transactions()
    assert len(result) == 1
    assert result[0].username == ("",)
    assert result[0].transaction_id != ""
    assert result[0].query == ["SHOW TRANSACTIONS;"]
    assert result[0].metadata == {}

