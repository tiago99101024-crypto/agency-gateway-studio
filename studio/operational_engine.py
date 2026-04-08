import uuid
from datetime import datetime, timedelta

TREND_HISTORY_MAX_ITEMS = 60
TREND_HISTORY_RETENTION_DAYS = 30
TREND_HISTORY_SOURCES = {"execution_state", "current_cycle", "migrated", "replay"}


def _ts():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _decide_creative_action(creative_data: dict) -> dict:
    performance_score = float(creative_data.get("performance_score", 0) or 0)
    penalty_strength = float(creative_data.get("penalty_strength", 0) or 0)
    confidence_score = float(creative_data.get("confidence_score", 0) or 0)
    stability_score = float(creative_data.get("stability_score", 0.5) or 0.5)
    id_recovered = bool(creative_data.get("_id_recovered", False))

    if performance_score > 75 and confidence_score > 0.6:
        action = "scale"
        budget_change = 0.3
    elif performance_score > 60:
        action = "maintain"
        budget_change = 0.0
    elif performance_score > 40:
        action = "test"
        budget_change = -0.2
    else:
        action = "kill"
        budget_change = -1.0

    if confidence_score < 0.3:
        if performance_score > 60:
            action = "maintain"
            budget_change = 0.0
        else:
            action = "test"
            budget_change = -0.2

    if penalty_strength > 0.7:
        action = "kill"
        budget_change = -1.0
    elif penalty_strength > 0.6 and action == "scale":
        action = "maintain" if performance_score > 60 else "test"
        budget_change = 0.0 if action == "maintain" else -0.2

    if id_recovered and action == "scale":
        action = "maintain"
        budget_change = 0.0

    priority = int((performance_score - (penalty_strength * 50)) * (0.5 + stability_score))
    if id_recovered:
        priority = int(priority * 0.7)
    reason = (
        f"performance_score={performance_score:.1f}, "
        f"penalty_strength={penalty_strength:.2f}, "
        f"confidence_score={confidence_score:.2f}, "
        f"stability_score={stability_score:.2f}, "
        f"id_recovered={id_recovered}"
    )
    return {
        "action": action,
        "budget_change": float(budget_change),
        "priority": priority,
        "reason": reason,
        "_action_engine": {
            "performance_score": performance_score,
            "penalty_strength": penalty_strength,
            "confidence_score": confidence_score,
            "stability_score": stability_score,
            "_id_recovered": id_recovered,
        },
    }


def _apply_missing_creative_id_guard(card: dict, operational_decision: dict) -> tuple[dict, dict]:
    operational_decision = dict(operational_decision or {})
    if card.get("creative_id"):
        card["_missing_creative_id"] = False
        return card, operational_decision

    card["_missing_creative_id"] = True
    operational_decision["action"] = "kill"
    operational_decision["budget_change"] = -1.0
    operational_decision["priority"] = 0
    operational_decision["reason"] = (
        (operational_decision.get("reason", "") + " | " if operational_decision.get("reason") else "")
        + "creative_id ausente"
    )

    card["priority"] = 0
    card["allocated_budget"] = 0.0
    card["budget_share"] = 0.0
    card["portfolio_action"] = "descartar"
    card["portfolio_decision"] = "descartar"
    return card, operational_decision


def _portfolio_rank_key(item: dict):
    operational = item.get("operational_decision", {}) or {}
    return (
        int(operational.get("priority", 0) or 0),
        int(item.get("portfolio_score", 0) or 0),
    )


def _should_refresh_allocation(card: dict, new_priority: int) -> bool:
    last_updated = str((card or {}).get("allocation_last_updated_at", "") or "").strip()
    previous_priority = int((card or {}).get("_previous_allocation_priority", new_priority) or new_priority)
    if not last_updated:
        return True
    if abs(int(new_priority or 0) - previous_priority) >= 20:
        return True
    try:
        last_dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
    except ValueError:
        return True
    now_dt = datetime.fromisoformat(_ts().replace("Z", "+00:00"))
    return (now_dt - last_dt) >= timedelta(hours=6)


def _allocate_creative_budget(creatives: list[dict], total_budget: float, exploration_envelope: float = 0.12) -> list[dict]:
    action_weights = {
        "scale": 1.0,
        "maintain": 0.6,
        "test": 0.3,
        "kill": 0.0,
    }
    max_share = 0.4
    min_test_share = 0.05

    normalized_budget = float(total_budget or 0.0)
    prepared_items = []
    performance_indexes = []
    exploration_indexes = []

    for idx, creative in enumerate(creatives or []):
        item = dict(creative)
        operational = item.get("operational_decision", {}) or {}
        action = (operational.get("action") or "").lower()
        priority = max(int(operational.get("priority", 0) or 0), 0)
        base_weight = action_weights.get(action, 0.0)
        effective_weight = 0.0 if action == "kill" or priority == 0 else (base_weight * priority)
        budget_key = item.get("_budget_key")
        if not budget_key:
            creative_id = item.get("creative_id") or item.get("id")
            if creative_id:
                budget_key = creative_id
            else:
                budget_key = item.get("_budget_key") or str(uuid.uuid4())
        item["_budget_key"] = budget_key
        item.setdefault("allocated_budget", 0.0)
        item.setdefault("budget_share", 0.0)
        refresh_allocation = _should_refresh_allocation(item, priority)
        item["_refresh_allocation"] = refresh_allocation
        prepared_items.append({
            "item": item,
            "action": action,
            "priority": priority,
            "weight": effective_weight,
            "refresh_allocation": refresh_allocation,
        })
        if action in {"scale", "maintain"} and effective_weight > 0 and refresh_allocation:
            performance_indexes.append(len(prepared_items) - 1)
        elif action == "test" and effective_weight > 0 and refresh_allocation:
            exploration_indexes.append(len(prepared_items) - 1)

    now_ts = _ts()
    review_due_ts = (datetime.fromisoformat(now_ts.replace("Z", "+00:00")) + timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%SZ")
    locked_share_total = 0.0
    for entry in prepared_items:
        item = entry["item"]
        if entry["refresh_allocation"]:
            continue
        existing_share = float(item.get("budget_share", 0.0) or 0.0)
        existing_allocated = float(item.get("allocated_budget", 0.0) or 0.0)
        if existing_share <= 0 and normalized_budget > 0 and existing_allocated > 0:
            existing_share = existing_allocated / normalized_budget
        existing_share = max(existing_share, 0.0)
        item["budget_share"] = round(existing_share, 6)
        item["allocated_budget"] = round(normalized_budget * existing_share, 2) if normalized_budget > 0 else 0.0
        locked_share_total += existing_share

    if normalized_budget <= 0:
        for entry in prepared_items:
            entry["item"]["allocated_budget"] = 0.0
            entry["item"]["budget_share"] = 0.0
        return [entry["item"] for entry in prepared_items]

    total_weight = sum(prepared_items[idx]["weight"] for idx in performance_indexes + exploration_indexes)
    if locked_share_total >= 1.0 or total_weight <= 0 or not (performance_indexes or exploration_indexes):
        total_existing_share = sum(float(entry["item"].get("budget_share", 0.0) or 0.0) for entry in prepared_items)
        if total_existing_share > 0:
            for entry in prepared_items:
                share = float(entry["item"].get("budget_share", 0.0) or 0.0) / total_existing_share
                entry["item"]["budget_share"] = round(share, 6)
                entry["item"]["allocated_budget"] = round(normalized_budget * share, 2)
        return [entry["item"] for entry in prepared_items]

    available_share_budget = max(0.0, 1.0 - locked_share_total)
    normalized_exploration_envelope = max(0.05, min(0.25, float(exploration_envelope or 0.12)))
    performance_budget = available_share_budget
    exploration_budget = 0.0
    if exploration_indexes:
        if performance_indexes:
            exploration_budget = min(available_share_budget, available_share_budget * normalized_exploration_envelope)
        else:
            exploration_budget = available_share_budget
        performance_budget = max(0.0, available_share_budget - exploration_budget)

    def _allocate_pool(
        pool_indexes: list[int],
        pool_budget: float,
        lower_bound_value: float,
        enforce_monotonic: bool,
    ) -> dict[int, float]:
        if pool_budget <= 0 or not pool_indexes:
            return {idx: 0.0 for idx in pool_indexes}

        effective_max_share = max(max_share, (1.0 / len(pool_indexes)))
        lower_bounds = {}
        upper_bounds = {}
        shares = {}
        for idx in pool_indexes:
            lower_bounds[idx] = min(lower_bound_value, pool_budget)
            upper_bounds[idx] = min(effective_max_share, pool_budget)
            shares[idx] = lower_bounds[idx]

        total_lower_bound = sum(lower_bounds.values())
        if total_lower_bound >= pool_budget:
            if total_lower_bound > 0:
                for idx in pool_indexes:
                    shares[idx] = (lower_bounds[idx] / total_lower_bound) * pool_budget
            else:
                for idx in pool_indexes:
                    shares[idx] = 0.0
        else:
            remaining_share = pool_budget - total_lower_bound
            free_indexes = {idx for idx in pool_indexes if shares[idx] < upper_bounds[idx]}
            while free_indexes and remaining_share > 1e-9:
                free_weight = sum(prepared_items[idx]["weight"] for idx in free_indexes)
                if free_weight <= 0:
                    break
                capped_indexes = []
                for idx in list(free_indexes):
                    proposed_extra = remaining_share * (prepared_items[idx]["weight"] / free_weight)
                    proposed_share = shares[idx] + proposed_extra
                    if proposed_share >= upper_bounds[idx]:
                        capped_indexes.append(idx)
                if not capped_indexes:
                    for idx in free_indexes:
                        shares[idx] += remaining_share * (prepared_items[idx]["weight"] / free_weight)
                    remaining_share = 0.0
                    break
                for idx in capped_indexes:
                    remaining_share -= max(upper_bounds[idx] - shares[idx], 0.0)
                    shares[idx] = upper_bounds[idx]
                    free_indexes.discard(idx)

                if remaining_share < 0:
                    remaining_share = 0.0

            if remaining_share > 1e-9 and pool_indexes:
                fallback_indexes = [idx for idx in pool_indexes if shares[idx] > 0] or list(pool_indexes)
                fallback_total = sum(prepared_items[idx]["weight"] for idx in fallback_indexes) or float(len(fallback_indexes))
                for idx in fallback_indexes:
                    base = prepared_items[idx]["weight"] if fallback_total > 0 else 1.0
                    shares[idx] += remaining_share * (base / fallback_total)

        total_share = sum(shares.values())
        if total_share > 0:
            for idx in pool_indexes:
                shares[idx] = (shares[idx] / total_share) * pool_budget

        if enforce_monotonic:
            ordered_by_weight = sorted(
                pool_indexes,
                key=lambda idx: (prepared_items[idx]["weight"], prepared_items[idx]["priority"]),
                reverse=True,
            )
            epsilon = 0.0001
            for pos in range(len(ordered_by_weight) - 1):
                higher_idx = ordered_by_weight[pos]
                lower_idx = ordered_by_weight[pos + 1]
                if prepared_items[higher_idx]["weight"] <= prepared_items[lower_idx]["weight"]:
                    continue
                if shares.get(higher_idx, 0.0) > shares.get(lower_idx, 0.0):
                    continue
                recipient_idx = None
                for candidate_idx in reversed(ordered_by_weight):
                    if candidate_idx == lower_idx:
                        continue
                    if shares.get(candidate_idx, 0.0) + epsilon <= upper_bounds.get(candidate_idx, pool_budget):
                        recipient_idx = candidate_idx
                        break
                if recipient_idx is None:
                    continue
                if shares.get(lower_idx, 0.0) - epsilon < lower_bounds.get(lower_idx, 0.0):
                    continue
                shares[lower_idx] -= epsilon
                shares[recipient_idx] += epsilon

        delta = round(pool_budget - sum(shares.values()), 6)
        if abs(delta) > 0 and pool_indexes:
            target_idx = max(pool_indexes, key=lambda idx: shares.get(idx, 0.0))
            shares[target_idx] = max(0.0, shares.get(target_idx, 0.0) + delta)

        rounded_total = round(sum(round(shares.get(idx, 0.0), 6) for idx in pool_indexes), 6)
        rounded_delta = round(pool_budget - rounded_total, 6)
        if abs(rounded_delta) > 0 and pool_indexes:
            target_idx = max(pool_indexes, key=lambda idx: shares.get(idx, 0.0))
            shares[target_idx] = max(0.0, shares.get(target_idx, 0.0) + rounded_delta)

        return shares

    performance_shares = _allocate_pool(
        performance_indexes,
        performance_budget,
        lower_bound_value=0.0,
        enforce_monotonic=True,
    )
    exploration_shares = _allocate_pool(
        exploration_indexes,
        exploration_budget,
        lower_bound_value=min_test_share,
        enforce_monotonic=False,
    )

    for idx, share in {**performance_shares, **exploration_shares}.items():
        share = max(share, 0.0)
        prepared_items[idx]["item"]["budget_share"] = round(share, 6)
        prepared_items[idx]["item"]["allocated_budget"] = round(normalized_budget * share, 2)
        prepared_items[idx]["item"]["allocation_last_updated_at"] = now_ts
        prepared_items[idx]["item"]["allocation_review_due"] = review_due_ts

    return [entry["item"] for entry in prepared_items]


def _is_active_creative(card: dict) -> bool:
    operational = (card or {}).get("operational_decision", {}) or {}
    action = (operational.get("action") or "").lower()
    return bool(
        (card or {}).get("creative_id")
        and not (card or {}).get("_missing_creative_id", False)
        and action in {"scale", "maintain", "test"}
    )


def _is_new_creative(card: dict) -> bool:
    if not _is_active_creative(card):
        return False
    try:
        time_active_hours = float((card or {}).get("time_active_hours"))
    except (TypeError, ValueError):
        return False
    return time_active_hours < 24.0


def _classify_performance_trend(history: list[dict]) -> str:
    valid_records = []
    for item in history or []:
        if not isinstance(item, dict):
            continue
        value = item.get("performance_score")
        raw_ts = str(item.get("updated_at", "") or "").strip()
        try:
            score = float(value)
        except (TypeError, ValueError):
            continue
        if not raw_ts:
            continue
        try:
            updated_at = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        valid_records.append({"performance_score": score, "updated_at": updated_at})

    valid_records.sort(key=lambda item: item["updated_at"], reverse=True)
    if not valid_records:
        return "estavel"

    now_dt = datetime.fromisoformat(_ts().replace("Z", "+00:00"))
    current_window = [
        item for item in valid_records
        if (now_dt - item["updated_at"]) <= timedelta(days=7)
    ][:10]
    if not current_window:
        current_window = valid_records[:10]

    current_count = len(current_window)
    previous_window = valid_records[current_count:current_count + current_count]

    if current_count < 3 or len(previous_window) < 3:
        return "estavel"

    current_avg = sum(item["performance_score"] for item in current_window) / current_count
    previous_avg = sum(item["performance_score"] for item in previous_window) / len(previous_window)
    absolute_delta = current_avg - previous_avg
    relative_delta = 0.0 if previous_avg == 0 else (absolute_delta / previous_avg)

    if relative_delta <= -0.10 or absolute_delta <= -5.0:
        return "caindo"
    if relative_delta >= 0.10 or absolute_delta >= 5.0:
        return "subindo"
    return "estavel"


def _sanitize_trend_history(
    records: list[dict],
    max_items: int = TREND_HISTORY_MAX_ITEMS,
    retention_days: int = TREND_HISTORY_RETENTION_DAYS,
) -> list[dict]:
    sanitized_history = []
    seen_keys = set()
    now_dt = datetime.fromisoformat(_ts().replace("Z", "+00:00"))
    cutoff_dt = now_dt - timedelta(days=retention_days)

    for item in records or []:
        if not isinstance(item, dict):
            continue
        creative_id = str(item.get("creative_id", "") or "").strip()
        raw_ts = str(item.get("updated_at", "") or "").strip()
        cycle_id = str(item.get("cycle_id", "") or "").strip()
        source = str(item.get("source", "") or "").strip()
        try:
            performance_score = float(item.get("performance_score"))
        except (TypeError, ValueError):
            continue
        if not creative_id or not raw_ts:
            continue
        try:
            updated_at = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        if updated_at < cutoff_dt:
            continue
        normalized_source = source if source in TREND_HISTORY_SOURCES else "migrated"
        dedupe_key = (creative_id, raw_ts, cycle_id)
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        sanitized_history.append({
            "creative_id": creative_id,
            "performance_score": performance_score,
            "updated_at": raw_ts,
            "source": normalized_source,
            "cycle_id": cycle_id,
        })

    sanitized_history.sort(key=lambda item: (item["updated_at"], item.get("cycle_id", "")), reverse=True)
    return sanitized_history[:max_items]


def _build_trend_history(
    previous_history: list[dict],
    cards: list[dict],
    updated_at: str,
    cycle_id: str = "",
    max_items: int = TREND_HISTORY_MAX_ITEMS,
) -> list[dict]:
    sanitized_history = _sanitize_trend_history(previous_history, max_items=max_items)
    seen_keys = {
        (item["creative_id"], item["updated_at"], item.get("cycle_id", ""))
        for item in sanitized_history
    }

    for card in cards or []:
        if not _is_active_creative(card):
            continue
        creative_id = str(card.get("creative_id", "") or "").strip()
        try:
            performance_score = float(card.get("performance_score"))
        except (TypeError, ValueError):
            continue
        if not creative_id:
            continue
        effective_cycle_id = str(cycle_id or "").strip()
        dedupe_key = (creative_id, updated_at, effective_cycle_id)
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        sanitized_history.append({
            "creative_id": creative_id,
            "performance_score": performance_score,
            "updated_at": updated_at,
            "source": "current_cycle",
            "cycle_id": effective_cycle_id,
        })

    return _sanitize_trend_history(sanitized_history, max_items=max_items)


def _compute_exploration_envelope(
    cards: list[dict],
    performance_history: list[dict],
    previous_envelope: float = 0.12,
    refresh_allowed: bool = True,
) -> dict:
    previous_value = max(0.05, min(0.25, float(previous_envelope or 0.12)))
    if not refresh_allowed:
        return {
            "exploration_envelope": round(previous_value, 4),
            "target_envelope": round(previous_value, 4),
            "active_count": sum(1 for card in cards or [] if _is_active_creative(card)),
            "has_new_creative": any(_is_new_creative(card) for card in cards or []),
            "performance_trend": "estavel",
            "refresh_allowed": False,
        }

    active_cards = [card for card in cards or [] if _is_active_creative(card)]
    active_count = len(active_cards)
    has_new_creative = any(_is_new_creative(card) for card in active_cards)
    performance_trend = _classify_performance_trend(performance_history)

    target = 0.12
    if active_count <= 2:
        target += 0.06
    elif active_count <= 4:
        target += 0.03

    if has_new_creative:
        target += 0.04

    if performance_trend == "caindo":
        target += 0.05
    elif performance_trend == "subindo":
        target -= 0.04

    target = max(0.05, min(0.25, target))
    if target > previous_value:
        target = min(target, previous_value + 0.05)
    else:
        target = max(target, previous_value - 0.05)

    smoothed = (previous_value * 0.7) + (target * 0.3)
    smoothed = max(0.05, min(0.25, smoothed))
    return {
        "exploration_envelope": round(smoothed, 4),
        "target_envelope": round(target, 4),
        "active_count": active_count,
        "has_new_creative": has_new_creative,
        "performance_trend": performance_trend,
        "refresh_allowed": True,
    }
