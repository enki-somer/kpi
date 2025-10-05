import re

def detect_whatsapp_format(filepath):
    """Detect the exact WhatsApp export format"""
    print("="*70)
    print("WhatsApp Format Detector")
    print("="*70)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:50]  # First 50 lines
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    print(f"\n📄 File: {filepath}")
    print(f"📊 First 50 lines preview:\n")
    
    for i, line in enumerate(lines, 1):
        if line.strip():
            print(f"{i:3d}: {repr(line[:150])}")
    
    print(f"\n{'='*70}")
    print("Pattern Analysis:")
    print("="*70)
    
    # Test various patterns
    patterns = {
        "Pattern 1 (iOS/Android - brackets)": r'\[(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\]\s*([^:]+?):\s*(.+)',
        "Pattern 2 (Android - dash)": r'(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\s*[-–—]\s*([^:]+?):\s*(.+)',
        "Pattern 3 (WhatsApp Web)": r'(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\s*-\s*([^:]+?):\s*(.+)',
        "Pattern 4 (Special chars)": r'(\d{1,2}/\d{1,2}/\d{2,4})[,\s]+(\d{1,2}:\d{2}(?::\d{2})?)\s*[^\w\d]*\s*([^:]+?):\s*(.+)',
    }
    
    content = ''.join(lines)
    
    for name, pattern in patterns.items():
        matches = re.findall(pattern, content, re.MULTILINE)
        print(f"\n{name}")
        print(f"  Matches found: {len(matches)}")
        if matches:
            print(f"  ✅ Example match:")
            date, time, sender, msg = matches[0]
            print(f"     Date: {date}")
            print(f"     Time: {time}")
            print(f"     Sender: {sender}")
            print(f"     Message: {msg[:50]}...")
            
            # Show a few more examples
            if len(matches) > 1:
                print(f"\n  Additional samples:")
                for i, (d, t, s, m) in enumerate(matches[1:4], 2):
                    print(f"  {i}. {d} {t} - {s}: {m[:40]}...")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = 'zabbix_chat.txt'
    
    detect_whatsapp_format(filepath)
    
    print(f"\n{'='*70}")
    print("Next Steps:")
    print("="*70)
    print("1. Check which pattern matched your format")
    print("2. If none matched, share the output above")
    print("3. I'll create a custom parser for your exact format")