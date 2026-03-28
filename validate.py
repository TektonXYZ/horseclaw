#!/usr/bin/env python3
"""
HorseClaw Validation Script
Validates that all modules can be imported and basic functionality works.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from horseclaw import HorseClaw
        from agent_registry import AgentRegistry
        from fee_collector import FeeCollector
        from token_converter import TokenConverter
        from allocation_engine import AllocationEngine
        from transaction_logger import TransactionLogger
        from config import Config
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality."""
    print("\nTesting basic functionality...")
    try:
        from horseclaw import HorseClaw
        
        # Create instance
        horse = HorseClaw(language="en")
        
        # Register agent
        result = horse.register_agent("test", "Test Agent")
        assert result['success'], "Agent registration failed"
        
        # Collect fee
        result = horse.collect_fee("test", 100.00)
        assert result['success'], "Fee collection failed"
        
        # Convert to tokens
        result = horse.convert_fees_to_tokens(50.00)
        assert result['success'], "Token conversion failed"
        
        # Request tokens
        result = horse.request_tokens("test", "claude", 1000, "normal")
        assert result['status'] in ['approved', 'partial', 'rejected'], "Invalid allocation status"
        
        print("✓ Basic functionality works")
        return True
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bilingual():
    """Test bilingual support."""
    print("\nTesting bilingual support...")
    try:
        from horseclaw import HorseClaw
        
        horse_en = HorseClaw(language="en")
        horse_zh = HorseClaw(language="zh")
        
        assert horse_en.i18n('welcome') != horse_zh.i18n('welcome'), "Translations should differ"
        
        print("✓ Bilingual support works")
        return True
    except Exception as e:
        print(f"✗ Bilingual test failed: {e}")
        return False


def test_json_api():
    """Test JSON API."""
    print("\nTesting JSON API...")
    try:
        from horseclaw import HorseClaw
        import json
        
        horse = HorseClaw(language="en")
        
        # Test register via JSON
        request = json.dumps({
            "action": "register_agent",
            "agent_id": "json_test",
            "name": "JSON Test"
        })
        response = horse.process_json_request(request)
        data = json.loads(response)
        assert data['success'], "JSON API registration failed"
        
        print("✓ JSON API works")
        return True
    except Exception as e:
        print(f"✗ JSON API test failed: {e}")
        return False


def test_config():
    """Test configuration."""
    print("\nTesting configuration...")
    try:
        from config import Config
        
        config = Config()
        assert config.language == "en", "Default language should be en"
        assert config.get("allocation.reserve_percent") == 0.10, "Reserve percent should be 0.10"
        
        print("✓ Configuration works")
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False


def main():
    print("="*50)
    print("HorseClaw Validation Suite")
    print("="*50)
    
    tests = [
        test_imports,
        test_basic_functionality,
        test_bilingual,
        test_json_api,
        test_config,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if all(results):
        print("✓ All validations passed!")
        return 0
    else:
        print("✗ Some validations failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
