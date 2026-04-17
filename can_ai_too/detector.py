from signal_processing import *

def extract_signals(log):
    signals = {}

    for msg in log:
        can_id = msg["id"]
        data = msg["data"]

        for i in range(8):
            key = (can_id, i)
            if key not in signals:
                signals[key] = []
            signals[key].append(data[i])

    return [{"id": k[0], "byte": k[1], "values": v} for k, v in signals.items()]

def group_signals(signals):
    groups = []

    for s in signals:
        placed = False
        for g in groups:
            if cross_correlation(s["values"], g[0]["values"]) > 0.85:
                g.append(s)
                placed = True
                break
        if not placed:
            groups.append([s])

    return groups

def detect_signals(log):
    signals = extract_signals(log)

    for s in signals:
        s["type"] = classify_signal(s["values"])
        s["smooth"] = smoothness_score(s["values"])

    groups = group_signals(signals)

    results = []

    for g in groups:
        size = len(g)
        t = g[0]["type"]

        label = "unknown"

        if size == 4 and t == "smooth":
            label = "wheel_speed"
        elif size == 2 and t == "smooth":
            label = "accelerator"
        elif size == 1 and t == "very_smooth":
            label = "vehicle_speed"
        elif t == "binary":
            label = "brake_or_indicator"

        results.append({
            "label": label,
            "signals": g,
            "confidence": min(100, int(50 + size*10))
        })

    return results
