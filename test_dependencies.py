#!/usr/bin/env python3
"""
Dependency Test Script
Test if all required packages are available
"""

def test_imports():
    """Test all required imports"""
    print("🧪 Testing Dependencies...")
    print("=" * 40)
    
    imports = [
        ("streamlit", "st"),
        ("pandas", "pd"), 
        ("plotly.express", "px"),
        ("plotly.graph_objects", "go"),
        ("numpy", "np"),
        ("openpyxl", None),
        ("datetime", None),
        ("json", None),
        ("os", None)
    ]
    
    failed_imports = []
    
    for package, alias in imports:
        try:
            if alias:
                exec(f"import {package} as {alias}")
            else:
                exec(f"import {package}")
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    print("\n" + "=" * 40)
    
    if failed_imports:
        print(f"❌ Failed imports: {', '.join(failed_imports)}")
        print("\n💡 Install missing packages:")
        print("pip install -r requirements.txt")
        return False
    else:
        print("✅ All dependencies available!")
        return True

def test_data_loading():
    """Test if data files can be loaded"""
    print("\n📊 Testing Data Loading...")
    print("=" * 40)
    
    try:
        import pandas as pd
        
        # Test Excel loading
        df = pd.read_excel('support_analysis.xlsx', sheet_name='Issues')
        print(f"✅ Issues sheet: {len(df)} rows")
        
        df = pd.read_excel('support_analysis.xlsx', sheet_name='Messages')
        print(f"✅ Messages sheet: {len(df)} rows")
        
        df = pd.read_excel('support_analysis.xlsx', sheet_name='KPI Summary')
        print(f"✅ KPI Summary sheet: {len(df)} rows")
        
        return True
        
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 WhatsApp Dashboard Dependency Test")
    print("=" * 50)
    
    imports_ok = test_imports()
    data_ok = test_data_loading()
    
    print("\n" + "=" * 50)
    if imports_ok and data_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Ready for deployment!")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Please fix the issues above before deploying.")

if __name__ == "__main__":
    main()
