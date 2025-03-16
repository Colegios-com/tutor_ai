import asyncio
import random
import time
import uuid
from typing import Dict, List, Optional
from datetime import datetime

# Import your actual modules
from data.models import Message
from utilities.message_parser import verify_message_payload, build_user_message
from utilities.response_orchestrator import orchestrate_response

# Test Payloads
TEST_PAYLOADS = {
    "text_message": {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "15550224444",
                        "phone_number_id": "12345"
                    },
                    "contacts": [{
                        "profile": {
                            "name": "Test User"
                        },
                        "wa_id": "5215550081111"
                    }],
                    "messages": [{
                        "from": "5215550081111",
                        "id": "wamid.test123",
                        "timestamp": str(int(time.time())),
                        "text": {
                            "body": "Help me understand derivatives"
                        },
                        "type": "text"
                    }]
                }
            }]
        }]
    },
    "image_message": {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "15550224444",
                        "phone_number_id": "12345"
                    },
                    "contacts": [{
                        "profile": {
                            "name": "Test User"
                        },
                        "wa_id": "5215550081111"
                    }],
                    "messages": [{
                        "from": "5215550081111",
                        "id": "wamid.test123",
                        "timestamp": str(int(time.time())),
                        "type": "image",
                        "image": {
                            "mime_type": "image/jpeg",
                            "sha256": "test_hash",
                            "id": "test_image_id",
                            "url": "https://example.com/test.jpg"
                        }
                    }]
                }
            }]
        }]
    },
    "document_message": {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "15550224444",
                        "phone_number_id": "12345"
                    },
                    "contacts": [{
                        "profile": {
                            "name": "Test User"
                        },
                        "wa_id": "5215550081111"
                    }],
                    "messages": [{
                        "from": "5215550081111",
                        "id": "wamid.test123",
                        "timestamp": str(int(time.time())),
                        "type": "document",
                        "document": {
                            "filename": "test.pdf",
                            "mime_type": "application/pdf",
                            "sha256": "test_hash",
                            "id": "test_doc_id",
                            "url": "https://example.com/test.pdf"
                        }
                    }]
                }
            }]
        }]
    },
    "command_message": {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "15550224444",
                        "phone_number_id": "12345"
                    },
                    "contacts": [{
                        "profile": {
                            "name": "Test User"
                        },
                        "wa_id": "5215550081111"
                    }],
                    "messages": [{
                        "from": "5215550081111",
                        "id": "wamid.test123",
                        "timestamp": str(int(time.time())),
                        "text": {
                            "body": "/guia Create a study guide for calculus"
                        },
                        "type": "text"
                    }]
                }
            }]
        }]
    }
}

# Test message variations
TEXT_MESSAGES = [
    "Can you help me understand quantum mechanics?",
    "What is the difference between mitosis and meiosis?",
    "Explain the French Revolution",
    "How do I solve quadratic equations?",
    "What are the main themes in Shakespeare's Hamlet?",
]

class TestCase:
    def __init__(self, payload_type: str, message_variation: Optional[str] = None):
        self.payload_type = payload_type
        self.message_variation = message_variation
        self.start_time = None
        self.end_time = None
        self.success = False
        self.error = None
        self.response_time = None

    def get_payload(self) -> Dict:
        payload = TEST_PAYLOADS[self.payload_type].copy()
        
        if self.message_variation and self.payload_type == "text_message":
            payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"] = self.message_variation
        
        # Update timestamp and message ID to be unique
        message = payload["entry"][0]["changes"][0]["value"]["messages"][0]
        message["timestamp"] = str(int(time.time()))
        message["id"] = f"wamid.test{uuid.uuid4()}"
        
        return payload

async def run_test_case(test_case: TestCase) -> None:
    try:
        test_case.start_time = time.time()
        
        # Get the test payload
        payload = test_case.get_payload()
        
        # Verify payload
        if not verify_message_payload(payload):
            raise Exception("Invalid payload")
        
        # Build user message
        user_message = build_user_message(payload)
        
        # Mock subscription type for testing
        subscription_type = "unlimited"
        
        # Process message through orchestrator
        response_message, response = await orchestrate_response(user_message=user_message, subscription_type=subscription_type)
        
        if not response_message:
            raise Exception("No response generated")
        
        test_case.success = True
        
    except Exception as e:
        test_case.success = False
        test_case.error = str(e)
    
    finally:
        test_case.end_time = time.time()
        test_case.response_time = test_case.end_time - test_case.start_time

async def run_load_test(num_concurrent_tests: int) -> List[TestCase]:
    # Generate random test cases
    test_cases = []
    for _ in range(num_concurrent_tests):
        payload_type = random.choice(list(TEST_PAYLOADS.keys()))
        message_variation = random.choice(TEXT_MESSAGES) if payload_type == "text_message" else None
        test_cases.append(TestCase(payload_type, message_variation))
    
    # Run test cases concurrently
    tasks = [run_test_case(test_case) for test_case in test_cases]
    await asyncio.gather(*tasks)
    
    return test_cases

def print_test_results(test_cases: List[TestCase]) -> None:
    total_tests = len(test_cases)
    successful_tests = sum(1 for test in test_cases if test.success)
    failed_tests = total_tests - successful_tests
    
    total_time = sum(test.response_time for test in test_cases)
    avg_time = total_time / total_tests if total_tests > 0 else 0
    
    print("\n=== Load Test Results ===")
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Average Response Time: {avg_time:.2f} seconds")
    print("\nResponse Time Distribution:")
    
    # Calculate percentiles
    response_times = sorted(test.response_time for test in test_cases)
    if response_times:
        p50 = response_times[len(response_times) // 2]
        p90 = response_times[int(len(response_times) * 0.9)]
        p95 = response_times[int(len(response_times) * 0.95)]
        p99 = response_times[int(len(response_times) * 0.99)]
        
        print(f"50th percentile: {p50:.2f} seconds")
        print(f"90th percentile: {p90:.2f} seconds")
        print(f"95th percentile: {p95:.2f} seconds")
        print(f"99th percentile: {p99:.2f} seconds")
    
    print("\nErrors:")
    for test in test_cases:
        if not test.success:
            print(f"- {test.payload_type}: {test.error}")

async def main():
    num_tests = 10  # Adjust this number for different load scenarios
    print(f"Starting load test with {num_tests} concurrent requests...")
    
    test_cases = await run_load_test(num_tests)
    print_test_results(test_cases)

if __name__ == "__main__":
    asyncio.run(main()) 