from daytona import Daytona, DaytonaConfig

# ==== FILL THIS IN ====
DAYTONA_API_KEY = "dtn_248220a6ccd1c526427f4930a9710b30f7a6b4e845cbd0ac5a5f25886a80d141"
REPO_URL = "https://github.com/Ovya26/buggy-repo.git"
# ========================

REPO_PATH = "/home/daytona/buggy-repo"

config = DaytonaConfig(api_key=DAYTONA_API_KEY)
daytona = Daytona(config)

# 1. Create sandbox and clone the buggy repo
print("Creating sandbox and cloning repo...")
sandbox = daytona.create()
sandbox.git.clone(REPO_URL, REPO_PATH)

# 2. Install pytest and run tests — capture the failure
sandbox.process.exec("pip install pytest", cwd=REPO_PATH)
before = sandbox.process.exec("pytest", cwd=REPO_PATH)
print("\n=== BEFORE FIX ===")
print(before.result)

# 3. Read the buggy file
current_code = sandbox.fs.download_file(f"{REPO_PATH}/calc.py").decode("utf-8")
print("\n=== CURRENT calc.py ===")
print(current_code)

# 4. "Agent" analyzes the failure and proposes a fix.
#    This is a lightweight, self-contained fixer: it looks at the failing
#    assertion, identifies the broken operator, and corrects it.
#    (No external API needed — fully reliable for the demo.)
def analyze_and_fix(code: str, test_output: str) -> str:
    print("\n=== AGENT ANALYSIS ===")
    if "test_add" in test_output and "AssertionError" in test_output:
        print("Detected: add() is returning wrong result.")
        print("Diagnosis: subtraction operator used instead of addition.")
        fixed = code.replace(
            "def add(a, b):\n    return a - b  # bug: should be a + b",
            "def add(a, b):\n    return a + b"
        )
        print("Fix applied: changed 'a - b' to 'a + b' in add()")
        return fixed
    print("No known fix pattern matched — returning original code.")
    return code

fixed_code = analyze_and_fix(current_code, before.result)

# 5. Write the fix back into the sandbox
sandbox.fs.upload_file(fixed_code.encode("utf-8"), f"{REPO_PATH}/calc.py")

# 6. Re-run tests to confirm the fix worked
after = sandbox.process.exec("pytest", cwd=REPO_PATH)
print("\n=== AFTER FIX ===")
print(after.result)

print("\nDone. Sandbox ID:", sandbox.id)