# Rugpull Prediction Dataset Preparation

Welcome to the Rugpull Prediction Dataset Preparation repository. This repository contains scripts to prepare the dataset for the main project on rugpull prediction. The project aims to identify potential rugpull scams in cryptocurrency projects by analyzing various data points.

## Repository Contents

This repository contains the following two main files:

1. `1-pair.py`
2. `Main_labelling.ipynb`

### `1-pair.py`

This script is responsible for the initial data collection and preprocessing. It pairs relevant data points from various sources to create a foundational dataset for further analysis.

### `Main_labelling.ipynb`

This Jupyter Notebook is used to execute the data labeling process. It utilizes the dataset prepared by `1-pair.py` and applies various labeling techniques to categorize the data, making it ready for the rugpull prediction model.

## Usage

Follow the steps below to get started with preparing your dataset:

### Prerequisites

Ensure you have the following installed:

- Python 3.x
- Jupyter Notebook
- Required Python packages (listed in `requirements.txt`)

### Installation

1. Clone this repository to your local machine:

   bash
   git clone https://github.com/your-username/rugpull-prediction-dataset.git
   cd rugpull-prediction-dataset
   

2. Install the required Python packages:

   bash
   pip install -r requirements.txt
   

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any features, bug fixes, or improvements.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request


