import os
# Set mock API key for testing before importing modules that read it
os.environ["NVIDIA_NIM_API_KEY"] = "mock_key"

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import cognee
from app.layer1.schemas import NormalizedPayload
from app.layer2.evaluate import evaluate
from app.layer2.valence import ValenceResult
from app.layer2.kinetics import get_kinetic_params
from app.layer2.trace import CognitiveTrace

class MockRecallResult:
    def __init__(self, id, text, score=None, similarity_score=None):
        self.id = id
        self.text = text
        if score is not None:
            self.score = score
        if similarity_score is not None:
            self.similarity_score = similarity_score

@pytest.fixture
def sample_payload():
    return NormalizedPayload(
        text="test payload text",
        timestamp=1719782400.0,
        content_hash="mocked_hash_123"
    )

@pytest.mark.asyncio
@patch("app.layer2.router_logic.registry")
@patch("app.layer2.resonance.cognee")
@patch("app.layer2.router_logic.cognee")
async def test_resonance_above_threshold(mock_router_cognee, mock_resonance_cognee, mock_registry, sample_payload):
    # Mock recall to return a result with similarity score > 0.92
    mock_resonance_cognee.recall = AsyncMock(return_value=[
        MockRecallResult("node_123", "test payload text", score=0.95)
    ])
    mock_resonance_cognee.improve = AsyncMock()
    mock_router_cognee.remember = AsyncMock()
    mock_registry.upsert = AsyncMock()

    # Call evaluate
    result = await evaluate(sample_payload)

    # Check results
    assert result["action"] == "reinforced"
    assert result["hash"] == sample_payload.content_hash

    # Verify improve was called
    mock_resonance_cognee.improve.assert_called_once_with("node_123")
    # Verify remember and registry.upsert were NOT called
    mock_router_cognee.remember.assert_not_called()
    mock_registry.upsert.assert_not_called()

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
@patch("app.layer2.resonance.cognee")
@patch("app.layer2.router_logic.cognee")
@patch("app.layer2.router_logic.registry")
async def test_resonance_below_threshold_proceeds_to_scoring(
    mock_registry, mock_router_cognee, mock_resonance_cognee, mock_post, sample_payload
):
    # Mock recall to return a result with similarity score <= 0.92
    mock_resonance_cognee.recall = AsyncMock(return_value=[
        MockRecallResult("node_123", "test payload text", score=0.85)
    ])
    
    # Mock NIM response for valence scoring (score=3)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": json.dumps({"valence_score": 3, "reason": "some preference"})
            }
        }]
    }
    mock_post.return_value = mock_response

    # Mock remember in router
    mock_router_cognee.remember = AsyncMock()
    mock_registry.upsert = AsyncMock()

    # Call evaluate
    result = await evaluate(sample_payload)

    assert result["action"] == "stored_context"
    assert result["weight"] == 50.0
    assert result["decay_rate"] == 3.5
    # node_id must be the payload content_hash
    assert result["node_id"] == sample_payload.content_hash
    
    mock_router_cognee.remember.assert_called_once()
    mock_registry.upsert.assert_called_once()

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
@patch("app.layer2.resonance.cognee")
@patch("app.layer2.router_logic.cognee")
@patch("app.layer2.router_logic.registry")
async def test_score_1_dropped_entirely(
    mock_registry, mock_router_cognee, mock_resonance_cognee, mock_post, sample_payload
):
    mock_resonance_cognee.recall = AsyncMock(return_value=[])
    
    # Mock NIM response for valence scoring (score=1)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": json.dumps({"valence_score": 1, "reason": "junk chatter"})
            }
        }]
    }
    mock_post.return_value = mock_response

    mock_router_cognee.remember = AsyncMock()
    mock_registry.upsert = MagicMock(return_value=AsyncMock())

    # Call evaluate
    result = await evaluate(sample_payload)

    assert result["action"] == "dropped"
    # Ensure neither remember nor upsert is called for score=1
    mock_router_cognee.remember.assert_not_called()
    mock_registry.upsert.assert_not_called()

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
@patch("app.layer2.resonance.cognee")
@patch("app.layer2.router_logic.cognee")
@patch("app.layer2.router_logic.registry")
@pytest.mark.parametrize("score,expected_weight,expected_decay", [
    (2, 20.0, 10.0),
    (3, 50.0, 3.5),
    (4, 100.0, 1.0)
])
async def test_score_context_kinetics_and_registry(
    mock_registry, mock_router_cognee, mock_resonance_cognee, mock_post, score, expected_weight, expected_decay, sample_payload
):
    mock_resonance_cognee.recall = AsyncMock(return_value=[])
    
    # Mock NIM response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": json.dumps({"valence_score": score, "reason": f"context info {score}"})
            }
        }]
    }
    mock_post.return_value = mock_response

    mock_router_cognee.remember = AsyncMock()
    mock_registry.upsert = AsyncMock()

    # Call evaluate
    result = await evaluate(sample_payload)

    assert result["action"] == "stored_context"
    assert result["weight"] == expected_weight
    assert result["decay_rate"] == expected_decay
    # node_id must be the payload content_hash
    assert result["node_id"] == sample_payload.content_hash

    # Verify remember call
    mock_router_cognee.remember.assert_called_once()
    
    # Verify registry.upsert call and arguments
    mock_registry.upsert.assert_called_once()
    called_trace = mock_registry.upsert.call_args[0][0]
    assert isinstance(called_trace, CognitiveTrace)
    assert called_trace.node_id == sample_payload.content_hash
    assert called_trace.text == sample_payload.text
    assert called_trace.valence_score == score
    assert called_trace.weight_initial == expected_weight
    assert called_trace.decay_rate == expected_decay
    assert called_trace.reason == f"context info {score}"

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
@patch("app.layer2.resonance.cognee")
@patch("app.layer2.router_logic.cognee")
@patch("app.layer2.router_logic.registry")
async def test_score_5_no_contradiction(
    mock_registry, mock_router_cognee, mock_resonance_cognee, mock_post, sample_payload
):
    mock_resonance_cognee.recall = AsyncMock(return_value=[])
    
    # Mock NIM response for valence scoring (score=5)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": json.dumps({"valence_score": 5, "reason": "core rule directive"})
            }
        }]
    }
    mock_post.return_value = mock_response

    # Mock router recall (no existing rules)
    mock_router_cognee.recall = AsyncMock(return_value=[])
    
    mock_router_cognee.remember = AsyncMock()
    mock_router_cognee.improve = AsyncMock()
    mock_router_cognee.forget = AsyncMock()
    mock_registry.upsert = AsyncMock()

    # Call evaluate
    result = await evaluate(sample_payload)

    assert result["action"] == "stored_core_rule"
    assert result["node_id"] == sample_payload.content_hash
    assert result["replaced"] is None
    
    mock_router_cognee.forget.assert_not_called()
    mock_router_cognee.remember.assert_called_once()
    mock_router_cognee.improve.assert_called_once_with(sample_payload.content_hash)
    
    # Verify trace upserted with weight_initial=None and decay_rate=0.0
    mock_registry.upsert.assert_called_once()
    called_trace = mock_registry.upsert.call_args[0][0]
    assert called_trace.node_id == sample_payload.content_hash
    assert called_trace.valence_score == 5
    assert called_trace.weight_initial is None
    assert called_trace.decay_rate == 0.0

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
@patch("app.layer2.resonance.cognee")
@patch("app.layer2.router_logic.cognee")
@patch("app.layer2.router_logic.registry")
async def test_score_5_with_contradiction_assert_call_order(
    mock_registry, mock_router_cognee, mock_resonance_cognee, mock_post, sample_payload
):
    mock_resonance_cognee.recall = AsyncMock(return_value=[])
    
    # Mock existing rules in Cognee (query_text="core rules")
    existing_rule = MockRecallResult("old_node_abc", "never use postgres", score=0.99)
    mock_router_cognee.recall = AsyncMock(return_value=[existing_rule])
    
    # Mock NIM responses for both valence scoring and contradiction detection using side_effect
    async def mock_post_side_effect(url, **kwargs):
        json_data = kwargs.get("json", {})
        messages = json_data.get("messages", [])
        is_contradiction_check = any("contradict" in m.get("content", "").lower() for m in messages)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        if is_contradiction_check:
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": json.dumps({"contradicting_id": "old_node_abc"})
                    }
                }]
            }
        else:
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": json.dumps({"valence_score": 5, "reason": "core rule directive"})
                    }
                }]
            }
        return mock_response

    mock_post.side_effect = mock_post_side_effect
    
    mock_router_cognee.forget = AsyncMock()
    mock_router_cognee.remember = AsyncMock()
    mock_router_cognee.improve = AsyncMock()
    mock_registry.upsert = AsyncMock()
    
    # We will use a Manager to track call order strictly
    manager = MagicMock()
    manager.attach_mock(mock_router_cognee.forget, "forget")
    manager.attach_mock(mock_router_cognee.remember, "remember")
    manager.attach_mock(mock_router_cognee.improve, "improve")

    # Call evaluate
    result = await evaluate(sample_payload)

    assert result["action"] == "stored_core_rule"
    assert result["replaced"] == "old_node_abc"
    
    # Verify call order: forget must be called BEFORE remember
    calls = [call[0] for call in manager.mock_calls]
    assert "forget" in calls
    assert "remember" in calls
    assert calls.index("forget") < calls.index("remember")

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
@patch("app.layer2.resonance.cognee")
@patch("app.layer2.router_logic.cognee")
@patch("app.layer2.router_logic.registry")
async def test_nim_api_failure_defaults_to_score_2(
    mock_registry, mock_router_cognee, mock_resonance_cognee, mock_post, sample_payload
):
    mock_resonance_cognee.recall = AsyncMock(return_value=[])
    
    # Mock NIM response to fail
    mock_post.side_effect = Exception("NIM API offline")

    mock_router_cognee.remember = AsyncMock()
    mock_registry.upsert = AsyncMock()

    # Call evaluate
    result = await evaluate(sample_payload)

    assert result["action"] == "stored_context"
    assert result["weight"] == 20.0
    assert result["decay_rate"] == 10.0
    
    mock_router_cognee.remember.assert_called_once()
    mock_registry.upsert.assert_called_once()

@pytest.mark.asyncio
@patch("app.layer2.evaluate.check_resonance")
async def test_evaluate_exception_caught_and_logged(mock_check_resonance, sample_payload):
    # check_resonance raises exception
    mock_check_resonance.side_effect = Exception("Database error")

    # Call evaluate - should not raise exception
    result = await evaluate(sample_payload)

    assert result["action"] == "error"
    assert result["hash"] == sample_payload.content_hash
    assert "Database error" in result["error"]

def test_get_kinetic_params_invalid():
    with pytest.raises(ValueError):
        get_kinetic_params(1)
    with pytest.raises(ValueError):
        get_kinetic_params(5)
