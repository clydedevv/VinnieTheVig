#!/usr/bin/env python3
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.flows.enhanced_aigg_flow import EnhancedAIGGFlow

flow = EnhancedAIGGFlow()
result = flow.analyze_query('Will Elon Musk buy Twitter again?')
if result:
    flow.print_result(result)
else:
    print('❌ No result generated') 