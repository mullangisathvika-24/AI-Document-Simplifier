"""
Test Script for AI Document Simplifier
Run this to verify all core functionality works
"""

import sys
import io
from pathlib import Path

def test_imports():
    """Test that all required libraries are installed"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit as st
        print("  ✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"  ❌ Streamlit import failed: {e}")
        return False
    
    try:
        import fitz
        print("  ✅ PyMuPDF (fitz) imported successfully")
    except ImportError as e:
        print(f"  ❌ PyMuPDF import failed: {e}")
        return False
    
    try:
        import google.generativeai as genai
        print("  ✅ google-generativeai imported successfully")
    except ImportError as e:
        print(f"  ❌ google-generativeai import failed: {e}")
        return False
    
    try:
        import hashlib
        print("  ✅ hashlib (built-in) available")
    except ImportError as e:
        print(f"  ❌ hashlib import failed: {e}")
        return False
    
    return True


def test_app_structure():
    """Test that app.py exists and has correct structure"""
    print("\n🧪 Testing app structure...")
    
    app_path = Path("app.py")
    if not app_path.exists():
        print("  ❌ app.py not found!")
        return False
    print("  ✅ app.py exists")
    
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Check for critical functions
    required_functions = [
        "extract_text_from_pdf",
        "get_summary",
        "get_key_points",
        "get_file_hash",
        "main"
    ]
    
    for func in required_functions:
        if f"def {func}" in content:
            print(f"  ✅ Function '{func}' found")
        else:
            print(f"  ❌ Function '{func}' missing!")
            return False
    
    # Check for session state initialization
    if "st.session_state" in content:
        print("  ✅ Session state usage found")
    else:
        print("  ⚠️  Session state not found (may cause issues)")
    
    # Check for caching decorators
    if "@st.cache_data" in content:
        print("  ✅ Cache decorators found")
    else:
        print("  ⚠️  Cache decorators not found (performance impact)")
    
    # Check for error handling
    if "try:" in content and "except" in content:
        print("  ✅ Error handling (try-except) found")
    else:
        print("  ❌ No error handling found!")
        return False
    
    return True


def test_streamlit_config():
    """Test Streamlit configuration"""
    print("\n🧪 Testing Streamlit configuration...")
    
    try:
        import streamlit as st
        
        # These would be set in the actual app
        print("  ✅ Streamlit version:", st.__version__)
        
        # Check if page config is set (can't easily test without running)
        print("  ℹ️  Page config should be set in app (run to verify)")
        
        return True
    except Exception as e:
        print(f"  ❌ Streamlit config test failed: {e}")
        return False


def test_pdf_processing():
    """Test PDF processing function (basic validation)"""
    print("\n🧪 Testing PDF processing logic...")
    
    try:
        # Import the function
        import fitz
        
        # Test that we can create a minimal PDF
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Test PDF content")
        
        # Save to bytes
        pdf_bytes = doc.tobytes()
        doc.close()
        
        print("  ✅ Can create test PDF in memory")
        
        # Test that we can read it back
        test_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = test_doc[0].get_text()
        test_doc.close()
        
        if "Test PDF content" in text:
            print("  ✅ Can extract text from PDF")
        else:
            print("  ❌ Text extraction failed")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ PDF processing test failed: {e}")
        return False


def test_requirements_file():
    """Test that requirements.txt exists and is valid"""
    print("\n🧪 Testing requirements.txt...")
    
    req_path = Path("requirements.txt")
    if not req_path.exists():
        print("  ❌ requirements.txt not found!")
        return False
    print("  ✅ requirements.txt exists")
    
    with open(req_path, 'r') as f:
        requirements = f.read()
    
    required_packages = ['streamlit', 'PyMuPDF', 'google-generativeai']
    
    for package in required_packages:
        if package in requirements:
            print(f"  ✅ Package '{package}' listed")
        else:
            print(f"  ❌ Package '{package}' missing!")
            return False
    
    return True


def test_error_messages():
    """Test that error messages are user-friendly"""
    print("\n🧪 Testing error message quality...")
    
    with open("app.py", 'r') as f:
        content = f.read()
    
    # Check for user-friendly error messages
    if "st.error" in content:
        print("  ✅ st.error() used for error display")
    else:
        print("  ⚠️  No st.error() found")
    
    if "st.warning" in content:
        print("  ✅ st.warning() used for warnings")
    else:
        print("  ⚠️  No st.warning() found")
    
    # Check for specific error scenarios
    error_scenarios = [
        "Invalid API key",
        "corrupted",
        "network",
        "quota"
    ]
    
    for scenario in error_scenarios:
        if scenario.lower() in content.lower():
            print(f"  ✅ Handles '{scenario}' scenario")
        else:
            print(f"  ⚠️  '{scenario}' scenario not explicitly handled")
    
    return True


def run_all_tests():
    """Run all test functions"""
    print("=" * 60)
    print("🧪 AI Document Simplifier - Production Readiness Tests")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("App Structure", test_app_structure),
        ("Streamlit Config", test_streamlit_config),
        ("PDF Processing", test_pdf_processing),
        ("Requirements File", test_requirements_file),
        ("Error Messages", test_error_messages),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! App is ready for deployment.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix before deploying.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
