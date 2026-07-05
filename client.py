"""
seller-rating-optimizer-skill: Client SDK
Analyze marketplace seller ratings and generate improvement action plans.
"""
from __future__ import annotations
from typing import Optional

PLATFORM_THRESHOLDS = {
    "amazon": {"positive_pct": 90, "response_time_hours": 24, "late_shipment_rate": 4, "defect_rate": 1, "cancellation_rate": 2.5},
    "ebay":   {"positive_pct": 98, "response_time_hours": 24, "late_shipment_rate": 3, "defect_rate": 0.5, "cancellation_rate": 2},
    "shopee": {"positive_pct": 85, "response_time_hours": 12, "late_shipment_rate": 5, "defect_rate": 2, "cancellation_rate": 3},
    "etsy":   {"positive_pct": 95, "response_time_hours": 24, "late_shipment_rate": 3, "defect_rate": 1, "cancellation_rate": 1},
    "walmart":{"positive_pct": 95, "response_time_hours": 24, "late_shipment_rate": 4, "defect_rate": 1, "cancellation_rate": 2},
    "default":{"positive_pct": 90, "response_time_hours": 24, "late_shipment_rate": 4, "defect_rate": 1, "cancellation_rate": 2.5},
}

METRIC_WEIGHTS = {
    "positive_pct": 35,
    "defect_rate": 25,
    "late_shipment_rate": 20,
    "response_time_hours": 12,
    "cancellation_rate": 8,
}

ACTION_TEMPLATES = {
    "positive_pct": [
        "Send automated post-purchase review request emails 5-7 days after delivery.",
        "Resolve all neutral (3-star) reviews proactively with a follow-up message.",
        "Add a handwritten thank-you card or QR code review reminder with each shipment.",
    ],
    "defect_rate": [
        "Implement pre-shipment QC checklist for all orders.",
        "Audit top 10 SKUs for consistent defect patterns and source alternatives.",
        "Improve product packaging to reduce damage-related returns.",
    ],
    "late_shipment_rate": [
        "Set processing time to 1 day less than actual to create buffer.",
        "Switch to a faster fulfillment carrier for peak periods.",
        "Automate shipment confirmation and tracking number upload immediately after dispatch.",
    ],
    "response_time_hours": [
        "Set up an automated acknowledgment reply for all buyer messages within 1 hour.",
        "Use a mobile app to respond to messages outside office hours.",
        "Create templated replies for the 10 most common customer questions.",
    ],
    "cancellation_rate": [
        "Sync inventory in real-time to avoid overselling out-of-stock items.",
        "Add buffer stock alerts at 10 units remaining to pause listings proactively.",
        "Review and tighten stock forecasting to prevent cancellations due to stockouts.",
    ],
}

SENTIMENT_KEYWORDS = {
    "negative": ["damaged", "broken", "wrong", "late", "never arrived", "defective", "disappointed", "refund", "return", "fake"],
    "positive": ["love", "great", "perfect", "fast", "excellent", "recommend", "amazing", "quality", "happy"],
}


class SellerRatingClient:
    """
    SDK for analyzing and improving marketplace seller ratings.
    """

    def analyze(
        self,
        current_metrics: dict,
        platform: str = "amazon",
        recent_reviews: Optional[list[dict]] = None,
    ) -> dict:
        """
        Analyze seller metrics and generate improvement plan.

        Args:
            current_metrics: Dict with: overall_rating, positive_pct, response_time_hours,
                             late_shipment_rate, defect_rate, cancellation_rate.
            platform:        Marketplace platform name.
            recent_reviews:  List of {rating (int), text (str), resolved (bool)}.

        Returns:
            dict with rating_score, risk_flags, action_plan, projected_improvement
        """
        plat = platform.lower()
        thresholds = PLATFORM_THRESHOLDS.get(plat, PLATFORM_THRESHOLDS["default"])
        recent_reviews = recent_reviews or []

        # Score each metric
        metric_scores = {}
        risk_flags = []

        for metric, weight in METRIC_WEIGHTS.items():
            current_val = float(current_metrics.get(metric, 0))
            threshold = thresholds.get(metric, 90)

            if metric == "positive_pct":
                # Higher is better
                ratio = current_val / threshold
                metric_scores[metric] = min(ratio, 1.0) * weight
                if current_val < threshold:
                    risk_flags.append({"metric": metric, "current": current_val, "required": threshold, "gap": round(threshold - current_val, 1)})
            elif metric == "response_time_hours":
                # Lower is better
                ratio = threshold / max(current_val, 1)
                metric_scores[metric] = min(ratio, 1.0) * weight
                if current_val > threshold:
                    risk_flags.append({"metric": metric, "current": current_val, "required": threshold, "gap": round(current_val - threshold, 1)})
            else:
                # Lower is better (defect, late shipment, cancellation)
                ratio = threshold / max(current_val, 0.01)
                metric_scores[metric] = min(ratio, 1.0) * weight
                if current_val > threshold:
                    risk_flags.append({"metric": metric, "current": current_val, "required": threshold, "gap": round(current_val - threshold, 2)})

        rating_score = round(sum(metric_scores.values()), 1)

        # Review sentiment analysis
        review_summary = self._analyze_reviews(recent_reviews)

        # Action plan (prioritized by highest impact)
        action_plan = []
        risk_flags_sorted = sorted(risk_flags, key=lambda x: METRIC_WEIGHTS.get(x["metric"], 0), reverse=True)
        for flag in risk_flags_sorted:
            actions = ACTION_TEMPLATES.get(flag["metric"], [])
            for action in actions[:2]:
                action_plan.append({
                    "priority": "critical" if METRIC_WEIGHTS.get(flag["metric"], 0) >= 20 else "high",
                    "metric": flag["metric"],
                    "action": action,
                    "expected_impact": f"Close {flag['gap']} gap in {flag['metric']}",
                })

        # Always add review-based actions if needed
        if review_summary["negative_count"] > 0:
            action_plan.append({
                "priority": "high",
                "metric": "review_sentiment",
                "action": f"Address {review_summary['negative_count']} negative review(s) with personal resolution messages.",
                "expected_impact": "Convert negative to neutral or positive",
            })

        # Projected improvement
        projected_score = min(100, rating_score + len(risk_flags) * 4)
        projected_rating = min(5.0, float(current_metrics.get("overall_rating", 4.0)) + len(risk_flags) * 0.1)

        return {
            "platform": platform,
            "rating_score": rating_score,
            "rating_band": "Excellent" if rating_score >= 85 else "Good" if rating_score >= 70 else "At Risk" if rating_score >= 50 else "Critical",
            "metric_scores": {k: round(v, 1) for k, v in metric_scores.items()},
            "risk_flags": risk_flags,
            "review_summary": review_summary,
            "action_plan": action_plan[:6],
            "projected_improvement": {
                "projected_health_score": projected_score,
                "projected_rating": round(projected_rating, 2),
                "actions_required": len(action_plan),
            },
        }

    @staticmethod
    def _analyze_reviews(reviews: list[dict]) -> dict:
        if not reviews:
            return {"total": 0, "avg_rating": 0, "positive_count": 0, "negative_count": 0, "top_issues": []}
        ratings = [int(r.get("rating", 3)) for r in reviews]
        avg = sum(ratings) / len(ratings)
        neg = [r for r in reviews if int(r.get("rating", 5)) <= 2]
        pos = [r for r in reviews if int(r.get("rating", 1)) >= 4]
        issues = []
        for r in neg:
            text = str(r.get("text", "")).lower()
            for keyword in SENTIMENT_KEYWORDS["negative"]:
                if keyword in text and keyword not in issues:
                    issues.append(keyword)
        return {
            "total": len(reviews), "avg_rating": round(avg, 2),
            "positive_count": len(pos), "negative_count": len(neg),
            "unresolved_negatives": sum(1 for r in neg if not r.get("resolved")),
            "top_issues": issues[:3],
        }
