import json
def test_invalid_endpoint(client, h_principal):
    response = client.get("/other", headers=h_principal)
    assert response.status_code == 404
    assert response.json["error"] == "NotFound"

def test_ready_endpoint(client):
    """Test the ready endpoint returns correct status and includes time"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ready'
    assert 'time' in data