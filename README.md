# genpark-seller-rating-optimizer-skill

> **GenPark AI Agent Skill** -- Analyze marketplace seller ratings, identify issues, and generate prioritized action plans to improve scores.

## Features

- Platform-specific thresholds: Amazon, eBay, Shopee, Etsy, Walmart
- 5-metric weighted health score: positive %, defect rate, late shipment, response time, cancellation rate
- Risk flag detection with gap analysis
- Review sentiment analysis (negative keyword detection)
- Prioritized action plan (critical / high)
- Projected rating improvement estimate

## Quick Start

```python
from client import SellerRatingClient

client = SellerRatingClient()
result = client.analyze(
    current_metrics={"positive_pct": 87, "late_shipment_rate": 6, "defect_rate": 1.8, "response_time_hours": 18, "cancellation_rate": 2},
    platform="amazon",
)
print(f"Health: {result['rating_score']}/100 ({result['rating_band']})")
for action in result["action_plan"][:3]:
    print(f"  -> {action['action']}")
```

## Installation

```bash
python example_usage.py  # No external dependencies
```

---
Built by [GenPark](https://genpark.ai) | [alphaparkinc](https://github.com/alphaparkinc)
