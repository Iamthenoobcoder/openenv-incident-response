import json
import re
from typing import Optional, Dict, Any

def parse_action(text: str) -> Optional[Dict[str, Any]]:
    """Parses a JSON action from LLM output."""
    try:
        # Try to find JSON block
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(text)
    except Exception:
        return None
