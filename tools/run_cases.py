"""Run the made-up sample people through the no-model path and print the result.
Usage: python tools/run_cases.py > tests/results.txt"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api"))
import server  # noqa: E402

server.BACKEND = "none"
for sid, (_f, label) in server.SAMPLES.items():
    r = server.build_response({"sample": sid})
    print("==", label)
    print(r["remembrance"])
    print("sections:", [s["key"] for s in r["ofrenda"]["sections"]], "|", r["written_by"])
    print()
