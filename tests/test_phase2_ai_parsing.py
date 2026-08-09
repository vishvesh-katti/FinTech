import pytest
from unittest.mock import patch, MagicMock
from ai_parser import parse_single_transaction

@patch('ai_parser.client.chat.completions.create')
def test_llm_json_output(mock_create):
    # Mock the response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"clean_name": "Zomato", "category": "Food", "is_fixed_obligation": false}'
    mock_create.return_value = mock_response
    
    result = parse_single_transaction("UPI/ZOMATO/FOOD/ORDER9182")
    
    assert result["clean_name"] == "Zomato"
    assert result["category"] == "Food"
    assert result["is_fixed_obligation"] == False

@patch('ai_parser.client.chat.completions.create')
def test_fixed_obligation_flag(mock_create):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"clean_name": "HDFC Home Loan", "category": "Loan EMI", "is_fixed_obligation": true}'
    mock_create.return_value = mock_response
    
    result = parse_single_transaction("NEFT/HDFC HOME LOAN EMI/JAN")
    
    assert result["is_fixed_obligation"] == True
