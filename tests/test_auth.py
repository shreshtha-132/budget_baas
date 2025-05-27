import pytest
from fastapi import Header, HTTPException, status
from unittest.mock import patch
import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))


from main import get_current_user_id

@patch("main.auth.verify_id_token")
def test_get_current_user_id_success(mock_verify):
    #simulating valid decoded token
    mock_verify.return_value = {"uid":"user123"}

    uid = get_current_user_id("Bearer faketoken123")
    assert uid == "user123"

    mock_verify.assert_called_once_with("faketoken123")

def test_get_current_user_id_invalid_header():
    with pytest.raises(HTTPException) as exc:
        get_current_user_id("InvalidHeader no-bearer")

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


@patch("main.auth.verify_id_token")
def test_get_current_user_id_invalid_token(mock_verify):
    #simualating firebase throwring an error
    mock_verify.side_effect = Exception("Token invalid")

    with pytest.raises(HTTPException) as exc:
        get_current_user_id("Bearer broken-token")

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Invalid or expired token"