# concreteml-covid-classifier
Repository for an FHE-powered viral strain classification tool and web application implemented through Concrete-ML and Django

## Tips
- When using WSL, ensure as much as possible that your filenames contain no spaces since the current version of Concrete-ML (1.0x) on WSL does not account for spaces in filenames due to the different filesystem being used in WSL.

- If you can't fix your filenames without risking breaking several applications, it's recommended to finish training, compilation, and saving of your Concrete-ML model on the Docker container.
