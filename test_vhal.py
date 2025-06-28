#!/usr/bin/env python3

from server import summarize_vhal

def test_vhal_summarization():
    """Test the vHAL summarization functionality"""
    
    print("Testing vHAL summarization tool...")
    
    # Test question
    question = "What are vHAL properties and how do they work?"
    
    try:
        result = summarize_vhal(question)
        print(f"\nQuestion: {question}")
        print(f"\nAnswer:\n{result}")
        print("\n" + "="*80)
        print("vHAL summarization test completed successfully!")
        
    except Exception as e:
        print(f"Error testing vHAL summarization: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_vhal_summarization()
