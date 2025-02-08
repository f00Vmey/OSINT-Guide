import os
import sys
import time
import subprocess

def banner():
    print("\n")
    print("  ██████╗ ███████╗██╗███╗   ██╗████████╗")
    print(" ██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝")
    print(" ██║   ██║███████╗██║██╔██╗ ██║   ██║   ")
    print(" ██║   ██║╚════██║██║██║╚██╗██║   ██║   ")
    print(" ╚██████╔╝███████║██║██║ ╚████║   ██║   ")
    print("  ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝")
    print("          A guide for OSINT (tool overview.)\n")
    
def list_options():
    print("\nMake sure that you have read the guide so you know what you are doing!\n")
    print("[1] Automated OSINT data scraper.")
    print("[2] Phone Number tracer.")
    print("[S] Setup")

def execute_script(script_name):
    try:
        subprocess.run(['python', script_name], check=True)
    except subprocess.CalledProcessError:
        print(f"Error executing {script_name}")
    time.sleep(1)

def setup():
    os.chdir('..')
    os.system('del /Q dist')
    os.system('del /Q automated_osint.egg-info')
    os.system('del /Q build')
    os.system('python setup.py install')
    time.sleep(1)

def main():
    while True:
        os.chdir('scripts')  # Ensure we are in the scripts folder
        os.system('cls' if os.name == 'nt' else 'clear')
        banner()
        list_options()
        choice = input("\n >> ").strip().lower()

        if choice == '1':
            execute_script('automated-OSINT.py')
        elif choice == '2':
            execute_script('phonenum-OSINT.py')
        elif choice == 's':
            setup()
        else:
            print("Invalid option. Please choose [1], [2], or [S].")
            time.sleep(1)

if __name__ == '__main__':
    main()
