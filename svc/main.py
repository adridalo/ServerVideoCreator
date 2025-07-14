from tkinter import Frame, Tk, ttk

from svc.convert import setup_convert_tab
from svc.download import setup_download_tab


def main():
    root = Tk()
    root.title("ServerVideoCreator")
    root.geometry("1000x700")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Download
    download_tab = Frame(notebook)
    notebook.add(download_tab, text="Download")
    setup_download_tab(download_tab)

    # Convert
    convert_tab = Frame(notebook)
    notebook.add(convert_tab, text="Convert")
    setup_convert_tab(convert_tab)

    root.mainloop()

if __name__ == "__main__":
    main()