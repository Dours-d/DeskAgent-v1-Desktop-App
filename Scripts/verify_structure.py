from pathlib import Path
import sys

def verify_structure():
    base_dir = Path(__file__).parent.parent
    
    required_paths = [
        base_dir / "data" / ".csv" / "campaigns_master.csv",
        base_dir / "data" / "agent_notes.txt",
        base_dir / "data" / "config.txt",
        base_dir / "scripts" / "deskagent_v1.py",
        base_dir / "scripts" / "requirements.txt"
    ]
    
    print("Verifying DeskAgent v1 structure...")
    print("=" * 60)
    
    all_good = True
    for path in required_paths:
        if path.exists():
            print(f"✓ {path.relative_to(base_dir)}")
        else:
            print(f"✗ MISSING: {path.relative_to(base_dir)}")
            all_good = False
    
    print("=" * 60)
    
    if all_good:
        print("Structure verification PASSED!")
        print(f"\nKey paths:")
        print(f"CSV: {base_dir / 'data' / '.csv' / 'campaigns_master.csv'}")
        print(f"Notes: {base_dir / 'data' / 'agent_notes.txt'}")
        print(f"Config: {base_dir / 'data' / 'config.txt'}")
    else:
        print("Structure verification FAILED!")
        print("\nPlease create missing files/directories.")
    
    return all_good

if __name__ == "__main__":
    verify_structure()