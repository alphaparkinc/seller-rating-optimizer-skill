"""
example_usage.py -- Demonstrates the SellerRatingClient SDK.
"""
from client import SellerRatingClient

def main():
    client = SellerRatingClient()

    print("[Seller Rating Optimizer -- Amazon]")
    result = client.analyze(
        current_metrics={
            "overall_rating": 4.2,
            "positive_pct": 87.5,
            "response_time_hours": 18,
            "late_shipment_rate": 6.2,
            "defect_rate": 1.8,
            "cancellation_rate": 2.1,
        },
        platform="amazon",
        recent_reviews=[
            {"rating": 1, "text": "Item arrived damaged and broken. Very disappointed.", "resolved": False},
            {"rating": 2, "text": "Delivery was late by 2 weeks. Poor communication.", "resolved": True},
            {"rating": 5, "text": "Amazing product! Fast delivery and excellent quality.", "resolved": False},
            {"rating": 3, "text": "Product is okay but shipping was slow.", "resolved": False},
            {"rating": 5, "text": "Love it! Would definitely recommend to friends.", "resolved": False},
        ]
    )
    print(f"Health Score: {result['rating_score']}/100 ({result['rating_band']})")
    print(f"\nMetric Scores:")
    for metric, score in result["metric_scores"].items():
        print(f"  {metric:<25}: {score:.1f} pts")
    print(f"\nRisk Flags ({len(result['risk_flags'])} issues):")
    for flag in result["risk_flags"]:
        print(f"  [{flag['metric']}] Current: {flag['current']} | Required: <{flag['required']} | Gap: {flag['gap']}")
    print(f"\nReview Summary: {result['review_summary']}")
    print(f"\nAction Plan (Top {len(result['action_plan'])} Actions):")
    for i, action in enumerate(result["action_plan"], 1):
        print(f"  {i}. [{action['priority'].upper()}] {action['action']}")
    proj = result["projected_improvement"]
    print(f"\nProjected Improvement: Score {result['rating_score']} -> {proj['projected_health_score']} | Rating -> {proj['projected_rating']}")

if __name__ == "__main__":
    main()
