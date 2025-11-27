from tkinter import Frame, Tk, ttk

from svc.convert import setup_convert_tab
from svc.download import setup_download_tab
from svc.scale import setup_scale_tab

# Main function that runs entire application
def main():
    # Root Tkinter object
    root = Tk()
    # Tkinter window title
    root.title("ServerVideoCreator")
    # Tkinter window size
    root.geometry("1000x700")

    # Notebook used to store tabs
    notebook = ttk.Notebook(root)
    # Display notebook
    notebook.pack(fill="both", expand=True)

    # Download tab
    download_tab = Frame(notebook)
    # Add download tab to notebook
    notebook.add(download_tab, text="Download")
    # Setup download tab (initialize variables + UI components)
    setup_download_tab(download_tab)

    # Convert tab
    convert_tab = Frame(notebook)
    # Add convert tab to notebook
    notebook.add(convert_tab, text="Convert")
    # Setup convert tab (initialize variables + UI components)
    setup_convert_tab(convert_tab)

    scale_tab = Frame(notebook)
    notebook.add(scale_tab, text="Scale")
    setup_scale_tab(scale_tab)

    # Run Tkinter application
    root.mainloop()

# Application entry gateway
if __name__ == "__main__":
    main()