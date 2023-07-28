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

## System and Technical Architecture
This tool was developed using the following dependencies:
- **Pygubu and Pygubu-designer** - A “what you see is what you get" (WYSIWYG) GUI designer for the Python’s tkinter module, as well as CustomTkinter
- **Tkinter** - Standard Python interface to the Tk GUI toolkit
- **CustomTkinter** - A Python UI library based on tkinter that provides more modern UI widgets to allow for more up-to-date UI designs
- **Dashing** - Software tool for sketching similarities of genomes or sequencing datasets.
- **pandas** - Python software library for data manipulation and analysis
- **Concrete-ML** - Privacy-preserving FHE machine learning library built on Concrete
- **WSL2** - A Windows compatibility layer for Linux that enables running a Linux terminal environment on Windows without virtualization
- **scikit-learn** - Software machine learning library for the Python programming language
- **Django Framework** - Open source Python-based Model-View-Controller (MVC) web framework
- **Bootstrap** - Open-source CSS front-end development framework for web applications
- **Google Colab** - Cloud-based Jupyter notebook environment

System requirements for the tool include:
- **Operating System**: Linux or Windows Subsystem for Linux 2
- **Memory**: 4GB minimum
- **Storage space**: 7GB free disk space for Concrete-ML package and dependencies

## Tips
- When using WSL, ensure as much as possible that you're developing on the Linux filesystem to avoid issues with spaces in filenames.
- Alternatives to developing on WSL2 include:
  - Google Colab
  - Kaggle
  - Concrete-ML's Docker container
- In my experience, saved models only work with the version of Concrete-ML it was compiled and saved on.
  - If your models and Concrete-ML versions don't match, please compile and save a newer version of your model using the version you're using.
