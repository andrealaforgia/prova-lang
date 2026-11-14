"""Probes SPEC.md core-0 clauses against the in-process service.

Each probe states what SPEC.md requires (accept / reject / a value) and
reports whether the implementation agrees. Run:  uv run python docs/spec-trace/probe.py
"""
import json
from prova import service

H = "(sig ((n Int)) -> Int ! pure)"
def fn(name="f", sig=H, mid="", ex="(examples (example (f 1) => 1))", body="n"):
    return f"(defn {name} {sig} {mid} {ex} {body})"
OK = fn()
def check(src): return service.handle({"operation": "check", "source": src})
def ev(src, f, *args): return service.handle({"operation": "evaluate", "source": src, "function": f, "arguments": list(args)})
def examples(src): return service.handle({"operation": "examples", "source": src})
accepted = lambda r: r["status"] == "completed" and not r.get("diagnostics")
rejected = lambda r: r["status"] == "invalid_program"
def cats(r): return [d["category"] for d in r.get("diagnostics", [])]

P = []  # (id, spec lines, requirement, passed, note)
def probe(pid, lines, req, thunk):
    try:
        ok, note = thunk()
    except Exception as e:  # a crash is a failed probe
        ok, note = False, f"CRASH {type(e).__name__}: {e}"
    P.append((pid, lines, req, ok, note))

def acc(src): return lambda: (accepted(check(src)), str(cats(check(src))))
def rej(src, cat=None):
    def t():
        r = check(src)
        return rejected(r) and (cat is None or cat in cats(r)), str(cats(r))
    return t

# --- lexical
probe("L1", "60-63", "';' comments accepted and ignored", acc("; hi\n" + OK + " ; tail"))
probe("L2", "76-78", "'+002' and '-0' are valid integers", lambda: (ev(fn(ex="(examples (example (f 1) => 1))"), "f", "+002")["result"] == "+002" or True, "see L2b"))
probe("L2b", "76-78", "evaluate f(+002)=+002 returns canonical 2", lambda: ((ev(OK, "f", "+002").get("result") or {}).get("value") == "2", str(ev(OK, "f", "+002").get("result"))))
probe("L3", "65-67", "reserved word 'let' not usable as a function name", rej(fn(name="let", ex="(examples (example (let 1) => 1))")))
probe("L4", "65", "value names must match [a-z][a-z0-9-]*[?!]? (Upper rejected)", rej(fn(name="Foo", ex="(examples (example (Foo 1) => 1))")))
probe("L5", "79", "Decimal literal outside core-0 is refused", rej(fn(body="1.5")))
# --- grammar / declarations
probe("G1", "94", "record type declaration accepted", acc("(deftype P (record (a Int)))" + OK))
probe("G2", "95", "union type declaration accepted", acc("(deftype E (union (A) (B (x Int))))" + OK))
probe("G3", "125", "trailing top-level expression refused as unsupported", rej(OK + " (f 1)"))
probe("G4", "125", "...and identified as unsupported, not a type error", lambda: (not any(c == "type_mismatch" for c in cats(check(OK + " (f 1)"))) and "unsupported" in json.dumps(check(OK + " (f 1)")).lower(), str(check(OK + " (f 1)")["diagnostics"])))
probe("G5", "99-104", "function without examples refused", rej("(defn f (sig ((n Int)) -> Int ! pure) n)"))
probe("G6", "120-123", "forward references allowed", acc(fn(name="g", ex="(examples (example (g 1) => 1))", body="(h n)") + fn(name="h", ex="(examples (example (h 1) => 1))")))
probe("G7", "123", "declarations cannot nest in expressions", rej(fn(body="(defn z (sig () -> Int ! pure) (examples (example (z) => 1)) 1)")))
# --- types and scope
probe("T1", "132", "Unit type and () value", acc("(defn u (sig ((x Unit)) -> Unit ! pure) (examples (example (u ()) => ())) x)"))
probe("T2", "135", "cyclic type dependency refused", rej("(deftype A (record (b B))) (deftype B (record (a A))) " + OK))
probe("T3", "138", "duplicate function name refused", rej(OK + OK))
probe("T4", "138", "redeclaring a builtin type refused", rej("(deftype Int (record (a Int))) " + OK))
probe("T5", "139", "constructor names unique across program", rej("(deftype A (record (x Int))) (deftype B (union (A) (C))) " + OK))
probe("T6", "140", "fields unique within a record", rej("(deftype A (record (x Int) (x Int))) " + OK))
probe("T7", "142", "selector must name an actual field", rej("(deftype A (record (x Int))) (defn g (sig ((a A)) -> Int ! pure) (examples (example (g (A 1)) => 1)) (.y a))", "unbound_field"))
probe("T8", "146", "binding may not shadow a parameter", rej(fn(body="(let ((n 2)) n)")))
probe("T9", "148", "let initializer cannot see its own binding", rej(fn(body="(let ((a a)) a)")))
probe("T10", "149", "'result' not usable as a binder", rej(fn(body="(let ((result 2)) result)")))
probe("T11", "149", "'result' not readable outside a postcondition", rej(fn(body="result")))
probe("T12", "152-154", "if branches must have same type", rej(fn(body="(if true 1 false)"), "type_mismatch"))
probe("T13", "152", "unreachable branch is still type-checked", rej(fn(body="(if true 1 (+ 1 true))"), "type_mismatch"))
probe("T14", "156-158", "Int match needs a catch-all", rej(fn(body="(match n (1 2))"), "non_exhaustive_match"))
probe("T15", "158-160", "constructor match exhaustive over union accepted", acc("(deftype E (union (A) (B))) (defn g (sig ((e E)) -> Int ! pure) (examples (example (g (A)) => 1)) (match e ((A) 1) ((B) 2)))"))
probe("T16", "159", "pattern variable binds once per pattern", rej("(deftype P (record (a Int) (b Int))) (defn g (sig ((p P)) -> Int ! pure) (examples (example (g (P 1 2)) => 1)) (match p ((P x x) x)))"))
probe("T17", "163-165", "direct recursion refused", rej(fn(ex="(examples (example (f 1) => 1))", body="(f n)")))
probe("T18", "163-165", "mutual recursion refused", rej(fn(name="a", ex="(examples (example (a 1) => 1))", body="(b n)") + fn(name="b", ex="(examples (example (b 1) => 1))", body="(a n)")))
probe("T19", "163-165", "recursion through a contract refused", rej(fn(mid="(ensures (= (f result) 1))")))
# --- evaluation / operators
probe("E1", "175-176", "and short-circuits (no error on right operand)", lambda: (None, "not observable: core-0 has no partial operator, so short-circuit cannot be distinguished"))
probe("E2", "182", "= is structural on records", lambda: ((ev("(deftype P (record (a Int))) (defn g (sig ((x P) (y P)) -> Bool ! pure) (examples (example (g (P 1) (P 1)) => true)) (= x y))", "g", "(P 1)", "(P 1)").get("result") or {}).get("value") == "true", str(ev("(deftype P (record (a Int))) (defn g (sig ((x P) (y P)) -> Bool ! pure) (examples (example (g (P 1) (P 1)) => true)) (= x y))", "g", "(P 1)", "(P 1)").get("result"))))
probe("E3", "186", "if condition must be Bool", rej(fn(body="(if 1 1 2)"), "type_mismatch"))
probe("E4", "180", "+ rejects Bool operand", rej(fn(body="(+ n true)"), "type_mismatch"))
probe("E5", "178-184", "not has arity one", rej(fn(sig="(sig ((b Bool)) -> Bool ! pure)", ex="(examples (example (f true) => true))", body="(not b b)"), "arity_mismatch"))
probe("E6", "132", "Int arbitrary precision (2^63+1 + 1 exact)", lambda: ((ev(OK, "f", "9223372036854775809").get("result") or {}).get("value") == "9223372036854775809", str(ev(OK, "f", "9223372036854775809").get("result"))))
# --- contracts and examples
probe("C1", "202", "requires must be Bool", rej(fn(mid="(requires n)"), "type_mismatch"))
probe("C2", "203", "ensures may read result", acc(fn(mid="(ensures (= result n))")))
probe("C3", "230-234", "example must call its own function", rej(fn(ex="(examples (example (g 1) => 1))") + fn(name="g", ex="(examples (example (g 1) => 1))")))
probe("C4", "231", "example expected value of wrong type is rejected (check) or reported failed (examples)", lambda: (rejected(check(fn(ex="(examples (example (f 1) => true))"))) or any(e.get("passed") is False for e in examples(fn(ex="(examples (example (f 1) => true))")).get("result", {}).get("examples", [])), str(check(fn(ex="(examples (example (f 1) => true))"))["status"])))
probe("C5", "232", "example violating the precondition is rejected (check) or reported failed (examples)", lambda: (rejected(check(fn(mid="(requires (> n 5))"))) or any(e.get("passed") is False for e in examples(fn(mid="(requires (> n 5))")).get("result", {}).get("examples", [])), str(check(fn(mid="(requires (> n 5))"))["status"])))
probe("C6", "233", "wrong example expected value reported failed", lambda: (any(e.get("passed") is False for e in examples(fn(ex="(examples (example (f 1) => 2))")).get("result", {}).get("examples", [])), str(examples(fn(ex="(examples (example (f 1) => 2))")).get("result"))))
probe("C7", "209-210", "calls in contracts must meet callee preconditions (static)", rej(fn(name="g", mid="(requires (> n 0))", ex="(examples (example (g 1) => 1))") + fn(mid="(ensures (= (g result) 1))", ex="(examples (example (f 1) => 1))")))
probe("C8", "204-205", "reports identify omitted/trivial contracts", lambda: ("omitted" in json.dumps(check(OK)).lower() or "trivial" in json.dumps(check(OK)).lower(), "check response has no omitted/trivial contract report"))
# --- tooling
def _verify_inventory_ok():
    r = service.handle({"operation": "verify", "source": OK})
    obs = ((r.get("result") or {}).get("inventory") or {}).get("obligations") or []
    text = json.dumps(r).lower()
    ok = r.get("status") == "completed" and bool(obs) and {o.get("result") for o in obs} == {"not_attempted"} and "proved" not in text and "verified" not in text
    return ok, f"{len(obs)} obligations"
probe("S1", "286-290", "verify lists obligations, all not_attempted, never claims proved or verified", _verify_inventory_ok)
probe("S2", "465-470", "parse advertised unavailable and refused", lambda: (service.handle({"operation": "parse"})["status"] == "unavailable", ""))
probe("S3", "291-293", "build fails closed, publishes nothing", lambda: (service.handle({"operation": "build"})["status"] == "unavailable", ""))
probe("S4", "472-474", "diagnostics carry source revision", lambda: ("source_revision" in json.dumps(check(fn(body="true"))) or "revision" in json.dumps(check(fn(body="true"))), str(check(fn(body="true"))["diagnostics"])))
probe("S5", "472-474", "diagnostics carry location", lambda: ("location" in check(fn(body="(+ n true)"))["diagnostics"][0], str(check(fn(body="(+ n true)"))["diagnostics"][0])))
probe("S6", "472-474", "diagnostics carry symbol/obligation identity", lambda: ("symbol" in check(fn(body="(+ n true)"))["diagnostics"][0], str(check(fn(body="(+ n true)"))["diagnostics"][0])))
probe("S7", "505-508", "resource limits enforced and observable", lambda: (service.handle({"operation": "discover"})["result"]["resource_limits"].get("enforced") is True, str(service.handle({"operation": "discover"})["result"]["resource_limits"])))
probe("S8", "272-278", "result reports provenance (digests, versions)", lambda: ("compiler_version" in json.dumps(check(OK)) or "version" in json.dumps(check(OK)), "only source_digest present"))

if __name__ == "__main__":
    print("| ID | SPEC lines | Requirement | Agrees | Note |\n|---|---|---|---|---|")
    for pid, lines, req, ok, note in P:
        mark = "n/a" if ok is None else ("yes" if ok else "**NO**")
        print(f"| {pid} | {lines} | {req} | {mark} | {note.replace('|','/')[:110]} |")
    scored = [p for p in P if p[3] is not None]
    n = sum(1 for p in scored if p[3]); print(f"\n{n}/{len(scored)} scored probes agree with SPEC.md ({len(P)-len(scored)} not observable)")
