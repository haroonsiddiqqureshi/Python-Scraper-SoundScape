import subprocess
import sys
import time

# List of files to run in order
scripts_to_run = [
    "joox/master.py",
    "theconcert/master.py",
    "ticketier/master.py",
    "allticket/master.py"
]

def run_script(script_name):
    print("=" * 60)
    print(f"🚀 STARTING: {script_name}")
    print("=" * 60)
    
    try:
        # sys.executable ensures we use the same python environment
        # check=True will raise an error if the script fails
        result = subprocess.run([sys.executable, script_name], check=True)
        print(f"\n✅ FINISHED: {script_name} (Status: Success)")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERROR: {script_name} failed with exit code {e.returncode}")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR executing {script_name}: {e}")

if __name__ == "__main__":
    total_start = time.time()
    
    for script in scripts_to_run:
        run_script(script)
        
        # Cool down period between scripts to ensure Edge driver closes properly
        # and to free up RAM
        print("⏳ Waiting 5 seconds before next script...")
        time.sleep(5) 

    total_end = time.time()
    duration = total_end - total_start
    
    print("=" * 60)
    print(f"🎉 GRAND MASTER FINISHED.")
    print(f"⏱️ Total time elapsed: {duration:.2f} seconds")
    print("=" * 60)