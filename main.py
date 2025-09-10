from src.agents.coordinator import Coordinator
import sys

def save_output(filename, content):
    with open(f"outputs/{filename}", "w") as f:
        f.write(content)

if __name__ == "__main__":
    coord = Coordinator()
    # Simple Query
    response = coord.receive_query("What are the main types of neural networks?")
    save_output("simple_query.txt", response + "\n" + "\n".join([f"{k}: {v}" for k, v in coord.memory_agent.conversation_memory[-1].items() if k != "timestamp"]))
    print("Simple Query:", response)

    # Complex Query
    response = coord.receive_query("Research transformer architectures, analyze their computational efficiency, and summarize key trade-offs")
    save_output("complex_query.txt", response + "\n" + "\n".join([f"{k}: {v}" for k, v in coord.memory_agent.conversation_memory[-1].items() if k != "timestamp"]))
    print("Complex Query:", response)

    # Memory Test
    coord.memory_agent.process_message({
        "action": "store",
        "content": "Transformers are efficient for NLP.",
        "topics": ["transformer architectures"],
        "source": "mock_kb",
        "agent": "research",
        "confidence": 0.9
    })
    response = coord.receive_query("What did we learn about transformer architectures earlier?")
    save_output("memory_test.txt", response + "\n" + "\n".join([f"{k}: {v}" for k, v in coord.memory_agent.conversation_memory[-1].items() if k != "timestamp"]))
    print("Memory Test:", response)

    # Multi-step
    response = coord.receive_query("Find recent papers on reinforcement learning, analyze their methodologies, and identify common challenges")
    save_output("multi_step.txt", response + "\n" + "\n".join([f"{k}: {v}" for k, v in coord.memory_agent.conversation_memory[-1].items() if k != "timestamp"]))
    print("Multi-step:", response)

    # Collaborative
    response = coord.receive_query("Compare two machine-learning approaches and recommend which is better for our use case")
    save_output("collaborative.txt", response + "\n" + "\n".join([f"{k}: {v}" for k, v in coord.memory_agent.conversation_memory[-1].items() if k != "timestamp"]))
    print("Collaborative:", response)