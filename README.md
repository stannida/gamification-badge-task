# Technical Challenge: Consulting on Gamification Badge Criteria

An interactive dashboard using streamlit framework in python created for exploring the dataset with user engagement metrics.

## Installation
The repository can be set up locally using Docker or by using `pip` and `streamlit`.
1. Clone the repository
```
git clone https://github.com/stannida/gamification-badge-task.git
```
2. Copy the original csv file with the dataset into the resources folder and rename it to *Technical Challenge Data Analyst.csv*
3. Build a docker container (dashboard is a default name, you can replace it with your own suitable name)
```
docker build -t dashboard .
```
4. Run the container
```
docker run -p 8502:8502 dashboard
```

You can also run it locally without Docker by running the following commands instead of lines 3-4:
```
pip install -r requirements.txt
streamlit run dashboard.py
```

In both ways a browser window will be opened with the dashboard accessible at http://localhost:8502

## Privacy
This repository is created for private usage only and may not be forked or fully or partially re-used.
