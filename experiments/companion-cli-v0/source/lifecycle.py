"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Pure lifecycle planner. No filesystem mutation, installation, service or symlink switching.
"""
import re
MARKS=["EXPERIMENTAL","SYNTHETIC_ONLY","A0_SYNTHETIC","NOT VALIDATION OR PRODUCTION AUTHORIZATION"]
VERSION_RE=re.compile(r"0\.[0-9]+\.[0-9]+-exp\.[1-9][0-9]*")
PIN_RE=re.compile(r"[0-9a-f]{64}")
def validate_entry(entry):
    if type(entry) is not dict or set(entry)!={"version","seal"} or type(entry["version"]) is not str or not VERSION_RE.fullmatch(entry["version"]) or type(entry["seal"]) is not str or not PIN_RE.fullmatch(entry["seal"]):raise ValueError("VERSION_RECORD")
    return dict(entry)
def plan(state,action,candidate=None):
    if type(state) is not dict or set(state)!={"current","previous"}:raise ValueError("STATE")
    current=validate_entry(state["current"]) if state["current"] is not None else None
    previous=validate_entry(state["previous"]) if state["previous"] is not None else None
    if previous and (not current or previous["version"]==current["version"]):raise ValueError("STATE")
    if action=="install":
        if current or previous:raise ValueError("ALREADY_INSTALLED")
        desired={"current":validate_entry(candidate),"previous":None}
    elif action=="update":
        if not current or previous:raise ValueError("RECONCILE_PREVIOUS_FIRST")
        c=validate_entry(candidate)
        def key(e):return tuple(map(int,re.findall(r"[0-9]+",e["version"])))
        if key(c)<=key(current):raise ValueError("NON_INCREMENTAL_UPDATE")
        desired={"current":c,"previous":current}
    elif action=="rollback":
        if candidate is not None or not previous:raise ValueError("NO_ROLLBACK")
        desired={"current":previous,"previous":current}
    elif action=="uninstall":
        if candidate is not None or not current:raise ValueError("NOT_INSTALLED")
        desired={"current":None,"previous":None}
    elif action=="retire-previous":
        if candidate is not None or not previous:raise ValueError("NO_PREVIOUS")
        desired={"current":current,"previous":None}
    else:raise ValueError("ACTION")
    return {"labels":MARKS,"status":"PROPOSED_NOT_EXECUTED","action":action,"expected_state":{"current":current,"previous":previous},"desired_state":desired,"mutation":"NOT_PERFORMED","evidence":"PRESERVE","toolchain":"PRESERVE","authorization":"SEPARATE_REQUIRED"}
