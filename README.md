# concreteml-covid-classifier
Repository for an FHE-powered viral strain classification tool and web application implemented through Concrete-ML and Django. The model was compiled on WSL's Linux filesystem (to avoid issues with spaces in the directory and file names).

## Instructions
- For instructions on installation and use, please refer to the user manual in the "Documentation" folder.

## Virtual Machine .ova File
Users can also access a pre-installed and configured version of the classifier system by downloading the .ova file available at the following link: [https://drive.google.com/file/d/1OmmNJIEOzR2r4Wy_puAjJap37VheIjBJ/view?usp=sharing](https://drive.google.com/file/d/1OmmNJIEOzR2r4Wy_puAjJap37VheIjBJ/view?usp=sharing).

The .ova file can be imported into virtualization software such as Virtualbox for use. As the system requires the execution of AVX and AVX2 instructions, please ensure that Hyper-V is disabled on your host machine if you use the Windows operating system. Please follow these guides at [makeuseof.com](https://www.makeuseof.com/windows-11-disable-hyper-v/) and [learn.microsoft.com](https://learn.microsoft.com/en-us/troubleshoot/windows-client/application-management/virtualization-apps-not-work-with-hyper-v) to disable Hyper-V on Windows machines.

The access credentials for the VM are as follows:
- Username: student
- Password: bscs114

## Tips
- When using WSL, ensure as much as possible that your filenames contain no spaces since the current version of Concrete-ML (1.0x) on WSL does not account for spaces in filenames due to the different filesystem being used in WSL (Or ensure that your files are located on your Linux filesystem).
- If you can't fix your filenames without risking breaking several applications, it's recommended to finish training, compilation, and saving of your Concrete-ML model on the other platforms for using Concrete-ML (Google Colab, Kaggle, Docker container).
- In my experience, saved models only worked with the version of Concrete-ML it was compiled and saved on. If your models and Concrete-ML versions don't match, it might be better to compile and save a newer version of your model using the version you're using.
- This project does not contain a virtual environment or the libraries required to make the project run (yet). Make your own and install the packages mentioned in requirements.txt to get things going.
- This project DOES contain the Django files for the server-side app as well as the .py files for the client-side GUI application.
- The desktop client app was implemented using tkinter, customtkinter, and the pygubu suite (pygubu, pygubu-designer)
  - For allowing GUI apps on WSL, follow this guide (https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps)
    - install X11 apps
    - run "export DISPLAY=:0;" in bash
  - All required packages can be installed via pip
  - The pygubu suite is a WYISWYG editor for tk, ttk, and customtkinter.
