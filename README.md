# concreteml-covid-classifier
Repository for an FHE-powered viral strain classification tool and web application implemented through Concrete-ML and Django. The model was compiled on an older version of Concrete-ML accessed through Docker due to filename limitations for WSL (spaces in the username).

## Tips
- When using WSL, ensure as much as possible that your filenames contain no spaces since the current version of Concrete-ML (1.0x) on WSL does not account for spaces in filenames due to the different filesystem being used in WSL.

- If you can't fix your filenames without risking breaking several applications, it's recommended to finish training, compilation, and saving of your Concrete-ML model on the Docker container.

## Instructions
- This project does not contain a virtual environment or the libraries required to make the project run (yet). Make your own and install the packages mentioned in requirements.txt to get things going.
- THis project DOES contain the Django files for the app. Use those.
