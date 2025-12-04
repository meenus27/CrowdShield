"""
Authority micro-playbook with dispatch simulation and ETA overlay.
"""
import math
from datetime import timedelta

PLAYBOOKS = {
    "Local Authority": ["Issue public advisory", "Activate shelters", "Coordinate transport"],
    "First Responder": ["Dispatch ground team", "Prepare medical aid", "Coordinate with command"],
    "Community Leader": ["Open local shelter", "Broadcast instructions", "Assist elderly"]
}

def dispatch(role, origin, target, G):
    """
    Place resource and compute ETA based on routing length.
    origin/target are (lat,lon).
    """
    actions = PLAYBOOKS.get(role, PLAYBOOKS["Local Authority"])
    # compute distance roughly as haversine between origin and target
    lat1, lon1 = origin
    lat2, lon2 = target
    R = 6371000
    phi1 = math.radians(lat1); phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    dist_m = R*c
    # assume responder speed 15 km/h => 4.166 m/s
    speed = 4.166
    eta_seconds = dist_m / speed if speed > 0 else None
    eta = timedelta(seconds=int(eta_seconds)) if eta_seconds else None
    marker = {"role": role, "origin": origin, "target": target, "eta": str(eta), "distance_m": int(dist_m)}
    return {"actions": actions, "marker": marker}