# BotMichel
A Reinforcement Learning PPO based agent for the car soccer game Rocket League

## Requirements
rlgym
rlgym-tools
stable-baselines3
torch

Project Organization
------------

    ├── logs               <- Tensorboard logs for training runs
    │
    ├── models             <- Trained models
    │
    ├── src                <- Source code for use in this project.
    │   │
    │   ├── environment    <- Scripts to deal deal with/reset the environment.
    │   │
    │   ├── observers      <- Scripts for observations builders
    │   │    
    │   ├── parsers        <- Scripts for action parsers 
    │   │
    │   ├── rewards        <- Scripts for reward functions 
    │   │
    │   ├── state_setters   
    │   │
    │   └── utils
    │    
    ├── agent.py
    ├── appearance.cfg
    ├── bot.cfg
    ├── bot.py
    ├── config.ini         <- The configuration files from which to import the projects parameters.
    ├── LICENSE
    ├── README.md          <- The top-level README for this project.
    ├── requirements.txt   <- The requirements file
    ├── run_gui.py
    ├── run.py
    ├── train.bat
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── interm         <- Intermediate data that has been transformed
    │   ├── processed      <- The final, canonical data sets for modeling
    │   └── raw            <- The original, immutable data dump
    │
    ├── guide              <- A set of markdown files with documented best practices, guidelines and rools for collaborative projects
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g
    │                         `1.0-jqp-initial-data-exploration`
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment
    │
    └── da-project         <- Source code for use in this project.
        │
        ├── data           <- Scripts to download or generate data
        │   └── make_dataset.py
        │
        ├── features       <- Scripts to turn raw data into features for modeling
        │   └── build_features.py
        │
        ├── models         <- Scripts to train models and then use trained models to make
        │   │                 predictions
        │   ├── predict_model.py
        │   └── train_model.py
        │
        └── visualization  <- Scripts to create exploratory and results oriented visualizations
            └── visualize.py