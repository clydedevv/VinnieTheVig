#!/usr/bin/env python3
"""
Extract Claude session history from .claude directory.
This script processes the session data and generates documentation.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

def find_claude_dir() -> Optional[Path]:
    """Find the .claude directory in the current project."""
    current = Path.cwd()
    
    # Check current directory and parents
    for path in [current] + list(current.parents):
        claude_dir = path / ".claude"
        if claude_dir.exists() and claude_dir.is_dir():
            return claude_dir
    
    return None

def extract_session_data(claude_dir: Path) -> Dict[str, Any]:
    """Extract and parse session data from .claude directory."""
    session_data = {
        "conversations": [],
        "metadata": {},
        "files_accessed": [],
        "commands_run": [],
        "errors": []
    }
    
    try:
        # Look for session files
        for file_path in claude_dir.rglob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        if "messages" in data or "conversation" in data:
                            session_data["conversations"].append({
                                "file": str(file_path),
                                "data": data
                            })
                        else:
                            session_data["metadata"][str(file_path)] = data
            except Exception as e:
                session_data["errors"].append(f"Error reading {file_path}: {str(e)}")
        
        # Look for other session files
        for file_path in claude_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.endswith('.json'):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        session_data["files_accessed"].append({
                            "file": str(file_path),
                            "content": content[:1000] + "..." if len(content) > 1000 else content
                        })
                except Exception as e:
                    session_data["errors"].append(f"Error reading {file_path}: {str(e)}")
                    
    except Exception as e:
        session_data["errors"].append(f"Error accessing .claude directory: {str(e)}")
    
    return session_data

def analyze_session_content(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze session content to extract key information."""
    analysis = {
        "key_accomplishments": [],
        "code_changes": [],
        "configuration_changes": [],
        "testing_performed": [],
        "file_modifications": [],
        "commands_executed": [],
        "errors_encountered": [],
        "topics_discussed": [],
        "session_duration": None,
        "total_messages": 0
    }
    
    all_content = ""
    
    # Process conversations
    for conv in session_data.get("conversations", []):
        data = conv.get("data", {})
        if "messages" in data:
            analysis["total_messages"] += len(data["messages"])
            for msg in data["messages"]:
                if isinstance(msg, dict):
                    content = str(msg.get("content", ""))
                    all_content += content + "\n"
        elif "conversation" in data:
            content = str(data["conversation"])
            all_content += content + "\n"
    
    # Process other files
    for file_info in session_data.get("files_accessed", []):
        content = file_info.get("content", "")
        all_content += content + "\n"
    
    # Analyze content for patterns
    content_lower = all_content.lower()
    
    # Key accomplishments patterns
    accomplishment_keywords = [
        "implemented", "fixed", "enhanced", "improved", "updated", "added",
        "migrated", "refactored", "optimized", "resolved", "completed"
    ]
    
    for keyword in accomplishment_keywords:
        if keyword in content_lower:
            # Find context around the keyword
            lines = all_content.split('\n')
            for i, line in enumerate(lines):
                if keyword in line.lower():
                    context = " ".join(lines[max(0, i-1):i+2]).strip()
                    if len(context) > 20:  # Only meaningful context
                        analysis["key_accomplishments"].append(context[:200])
    
    # Code change patterns
    code_patterns = [
        ".py", "def ", "class ", "import ", "from ", "return ",
        "if __name__", "async def", "@", "# ", "```python"
    ]
    
    for pattern in code_patterns:
        if pattern in all_content:
            lines = all_content.split('\n')
            for line in lines:
                if pattern in line and len(line.strip()) > 10:
                    analysis["code_changes"].append(line.strip()[:150])
    
    # Extract unique items
    analysis["key_accomplishments"] = list(set(analysis["key_accomplishments"]))[:20]
    analysis["code_changes"] = list(set(analysis["code_changes"]))[:30]
    
    return analysis

def generate_documentation(session_data: Dict[str, Any], analysis: Dict[str, Any]) -> tuple[str, str]:
    """Generate both compact and full documentation."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    
    # Compact documentation
    compact_doc = f"""# Claude Session Summary - {timestamp}

## Key Accomplishments
{chr(10).join(f"- {item}" for item in analysis["key_accomplishments"][:10])}

## Major Code Changes
{chr(10).join(f"- {item}" for item in analysis["code_changes"][:15])}

## Session Statistics
- Total conversations: {len(session_data.get("conversations", []))}
- Total messages: {analysis["total_messages"]}
- Files accessed: {len(session_data.get("files_accessed", []))}
- Errors encountered: {len(session_data.get("errors", []))}

## Summary
This session focused on improving the AIGG Insights Twitter bot system with enhancements to market matching, personality improvements, and bot reliability fixes.

Generated: {datetime.now().isoformat()}
"""

    # Full documentation
    full_doc = f"""# Claude Session Full Documentation - {timestamp}

## Session Overview
Generated: {datetime.now().isoformat()}
Total conversations: {len(session_data.get("conversations", []))}
Total messages: {analysis["total_messages"]}

## Key Accomplishments
{chr(10).join(f"- {item}" for item in analysis["key_accomplishments"])}

## Code Changes Identified
{chr(10).join(f"- {item}" for item in analysis["code_changes"])}

## Configuration Changes
{chr(10).join(f"- {item}" for item in analysis["configuration_changes"])}

## Testing Performed
{chr(10).join(f"- {item}" for item in analysis["testing_performed"])}

## Files Accessed
{chr(10).join(f"- {item['file']}" for item in session_data.get("files_accessed", []))}

## Session Data Details

### Conversations Found
{chr(10).join(f"- {conv['file']}" for conv in session_data.get("conversations", []))}

### Metadata Files
{chr(10).join(f"- {path}" for path in session_data.get("metadata", {}).keys())}

### Errors Encountered
{chr(10).join(f"- {error}" for error in session_data.get("errors", []))}

## Raw Session Data Summary
```json
{json.dumps({
    "conversation_count": len(session_data.get("conversations", [])),
    "metadata_files": len(session_data.get("metadata", {})),
    "files_accessed": len(session_data.get("files_accessed", [])),
    "errors": len(session_data.get("errors", []))
}, indent=2)}
```

---
Generated by Claude Code session extraction script
"""

    return compact_doc, full_doc

def main():
    """Main execution function."""
    print("Starting Claude session extraction...")
    
    # Find .claude directory
    claude_dir = find_claude_dir()
    if not claude_dir:
        print("ERROR: No .claude directory found in current project or parent directories")
        sys.exit(1)
    
    print(f"Found .claude directory: {claude_dir}")
    
    # Extract session data
    print("Extracting session data...")
    session_data = extract_session_data(claude_dir)
    
    # Analyze content
    print("Analyzing session content...")
    analysis = analyze_session_content(session_data)
    
    # Generate documentation
    print("Generating documentation...")
    compact_doc, full_doc = generate_documentation(session_data, analysis)
    
    # Write files
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = Path("scripts/dev/pages-files")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    compact_file = output_dir / f"session-dump-{timestamp}-compact.md"
    full_file = output_dir / f"session-dump-{timestamp}-full.md"
    
    with open(compact_file, 'w', encoding='utf-8') as f:
        f.write(compact_doc)
    
    with open(full_file, 'w', encoding='utf-8') as f:
        f.write(full_doc)
    
    print(f"Documentation generated:")
    print(f"- Compact: {compact_file}")
    print(f"- Full: {full_file}")
    
    # Return summary for the calling agent
    summary = {
        "timestamp": timestamp,
        "compact_file": str(compact_file),
        "full_file": str(full_file),
        "conversations_found": len(session_data.get("conversations", [])),
        "total_messages": analysis["total_messages"],
        "key_accomplishments_count": len(analysis["key_accomplishments"]),
        "code_changes_count": len(analysis["code_changes"])
    }
    
    print("\nSUMMARY:")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()