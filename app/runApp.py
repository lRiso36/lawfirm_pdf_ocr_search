import streamlit.web.cli as stcli
import os, sys
import multiprocessing


def resolve_path(path):
    # This finds the "Secret Compartment" address
    try:
        base_path = sys._MEIPASS
    except Exception:
        # If not an EXE, just look in the main folder
        base_path = os.path.dirname(__file__)

    return os.path.join(base_path, path)


if __name__ == "__main__":
    multiprocessing.freeze_support()

    # This tells Streamlit exactly where search.py is hiding inside the EXE
    script_path = resolve_path("search.py")

    sys.argv = [
        "streamlit",
        "run",
        script_path,
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())
