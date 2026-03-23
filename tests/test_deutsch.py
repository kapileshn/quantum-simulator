import pytest
from simulation_engine.algorithms import deutsch

def test_deutsch_cases():
    # Case 1: Constant 0 -> Constant
    res1 = deutsch.run(1)
    assert res1['result'] == 'constant'
    assert res1['measurement'] == '0'

    # Case 2: Balanced (Identity) -> Balanced
    res2 = deutsch.run(2)
    assert res2['result'] == 'balanced'
    assert res2['measurement'] == '1'

    # Case 3: Balanced (NOT) -> Balanced
    res3 = deutsch.run(3)
    assert res3['result'] == 'balanced'
    assert res3['measurement'] == '1'

    # Case 4: Constant 1 -> Constant
    res4 = deutsch.run(4)
    assert res4['result'] == 'constant'
    assert res4['measurement'] == '0'

def test_deutsch_invalid_case():
    with pytest.raises(ValueError):
        deutsch.run(5)
