import sys
import os
import pytest
# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.coordinator import Coordinator

@pytest.fixture
def coordinator():
    return Coordinator()

def test_simple_query(coordinator):
    response = coordinator.receive_query("What are the main types of neural networks?")
    assert "Synthesized response" in response
    assert "No info found" in response or "neural networks" in response

def test_complex_query(coordinator):
    response = coordinator.receive_query("Research transformer architectures, analyze their computational efficiency, and summarize key trade-offs")
    assert "Synthesized response" in response
    assert "research" in response.lower() and "analysis" in response.lower()

def test_memory_test(coordinator):
    coordinator.memory_agent.process_message({
        "action": "store",
        "content": "Transformers are efficient for NLP.",
        "topics": ["transformer architectures"],
        "source": "mock_kb",
        "agent": "research",
        "confidence": 0.9
    })
    response = coordinator.receive_query("What did we learn about transformer architectures earlier?")
    assert "Synthesized response" in response
    assert "Transformers are efficient" in response

def test_multi_step(coordinator):
    response = coordinator.receive_query("Find recent papers on reinforcement learning, analyze their methodologies, and identify common challenges")
    assert "Synthesized response" in response
    assert "research" in response.lower() and "analysis" in response.lower()

def test_collaborative(coordinator):
    response = coordinator.receive_query("Compare two machine-learning approaches and recommend which is better for our use case")
    assert "Synthesized response" in response
    assert "analysis" in response.lower()