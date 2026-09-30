import math
from .models import DistrictPriority

CATEGORY_CRITICALITY = {
    "HEALTHCARE": 1.0,
    "WATER": 0.9,
    "SANITATION": 0.8,
    "ELECTRICITY": 0.7,
    "ROADS": 0.6,
    "EDUCATION": 0.5,
    "DIGITAL": 0.4
}

def calculate_priority_scores(requests: list, districts: list) -> list[DistrictPriority]:
    results = []
    
    # Pre-process district info
    district_map = {(d['name'], d['state']): d for d in districts}
    
    # Group requests by district
    req_by_dist = {}
    for req in requests:
        dist_key = (req['location_district'], req['location_state'])
        if dist_key not in req_by_dist:
            req_by_dist[dist_key] = []
        req_by_dist[dist_key].append(req)
        
    for dist_key, reqs in req_by_dist.items():
        district, state = dist_key
        dist_info = district_map.get(dist_key, {
            'population': 1000000, # default 1M
            'infra_index': 0.5 # default
        })
        
        total_reqs = len(reqs)
        population = max(1, dist_info['population'])
        
        # Calculate components
        demand_density_raw = (total_reqs / (population / 100000.0))
        demand_density = min(1.0, demand_density_raw / 10.0) # Assume 10 req/100k is max (1.0)
        
        infra_gap = 1.0 - dist_info['infra_index']
        
        population_weight = min(1.0, math.log10(max(10000, population)) / 8.0) # Assume 100M is max (8)
        
        avg_urgency = sum(r['urgency'] for r in reqs) / total_reqs
        urgency_factor = avg_urgency / 5.0
        
        # Category criticality
        cat_counts = {}
        for r in reqs:
            cat = r['category']
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
            
        avg_criticality = sum(CATEGORY_CRITICALITY.get(r['category'], 0.5) for r in reqs) / total_reqs
        
        # PREDICTIVE ANOMALY DETECTION
        # Detect rapid velocity of identical severe requests (Flash-Mob Complaints)
        anomaly_multiplier = 1.0
        if cat_counts:
            max_cat_count = max(cat_counts.values())
            if total_reqs >= 5 and (max_cat_count / total_reqs) > 0.6 and avg_urgency > 3.5:
                anomaly_multiplier = 1.25 # 25% Boost for critical clustering
        
        raw_score = (
            0.30 * demand_density +
            0.25 * infra_gap +
            0.20 * population_weight +
            0.15 * urgency_factor +
            0.10 * avg_criticality
        )
        
        priority_score = min(1.0, raw_score * anomaly_multiplier)
        
        top_issues = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)
        top_issues_names = [x[0] for x in top_issues[:3]]
        
        if anomaly_multiplier > 1.0 and len(top_issues_names) > 0:
            top_issues_names[0] = f"⚠️ THREAT CLUSTER: {top_issues_names[0]}"
        
        dp = DistrictPriority(
            district_name=district,
            state=state,
            priority_score=priority_score * 100.0, # 0-100 scale
            demand_density=demand_density,
            infra_gap=infra_gap,
            population_weight=population_weight,
            urgency_factor=urgency_factor,
            category_breakdown=cat_counts,
            total_requests=total_reqs,
            top_issues=top_issues_names
        )
        results.append(dp)
        
    results.sort(key=lambda x: x.priority_score, reverse=True)
    return results
