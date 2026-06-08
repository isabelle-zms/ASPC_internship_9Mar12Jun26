"""
rns_generator.py — Reticulum Instance & Identity Generator
===========================================================
 
Generates a Reticulum Instance (aka configpath) and Identity for future use.
 
Usage:
------
Run the script interactively:
 
    python3 rns_generator.py
 
You will be prompted for:
  - An output directory (where the generated files will be saved)
  - A name for the Instance config folder
  - A name for the Identity file
 
Requirements:
-------------
    pip install rns
 
Output structure (with default names):
---------------------------------------
    <your working directory>/
    └── gen_RNS/
        ├── .gen_reticulum/   ← Reticulum instance (config directory)
        └── gen_identity      ← Reticulum identity (cryptographic key file)
"""


import RNS
import argparse
import os

def main():
    # ── Welcome banner ────────────────────────────────────────────────────────
    print("="*55 + "\n      Reticulum Instance & Identity Generator\n" + "="*55)

    # ── Show the working directory so the user knows where relative paths land ─
    cwd = os.getcwd()
    print(f"\n📂 Current Working Directory (CWD)\n   {cwd}")

    output_directory = input("\nOutput directory relative to CWD (default: 'gen_RNS')\n> ")
    os.makedirs(output_directory, exist_ok=True)

    # ── Step 1: Reticulum Instance ────────────────────────────────────────────
    print("\n" + "━"*55 + "\n 1. Generate Reticulum Instance (i.e., config path)\n" + "━"*55)
    instance_out = input("\nGenerated Instance file name (default: '.gen_reticulum')\n>  ") or ".gen_reticulum"
    print("\nGenerating instance... RNS warnings should appear below")
    # RNS may print startup warnings here (e.g. "No interfaces configured").
    # These are normal for a freshly created instance and can be ignored.
    generate_instance(os.path.join(output_directory, instance_out))
    print("\n✓ Instance generated successfully at path:", os.path.join(cwd, output_directory, instance_out))

    # ── Step 2: Reticulum Identity ────────────────────────────────────────────
    print("\n" + "━"*55 + "\n 2. Generate Reticulum Identity\n" + "━"*55)
    identity_out = input("\nGenerated Identity file name (default: 'gen_identity')\n>  ") or "gen_identity"
    generate_identity(os.path.join(output_directory, identity_out))
    print("\n✓ Identity generated successfully at path:", os.path.join(cwd, output_directory, identity_out))

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "="*55 + "\n      Setup Complete!\n" + "="*55)
    print(f"""
Output Summary:

{cwd}
└── /{output_directory}
    ├── /{instance_out}
    └── {identity_out}

Happy coding @ ASPC! :)
    """)
    

def generate_instance(instancepath):
    reticulum = RNS.Reticulum(instancepath)


def generate_identity(identitypath):
    identity = RNS.Identity()
    identity.to_file(identitypath)


main()
