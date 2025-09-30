# visualization_for_strava

## What is this?

**able to analysis for my activites**

<img width="767" height="742" alt="スクリーンショット 2025-09-30 18 29 13" src="https://github.com/user-attachments/assets/9ec05641-d87f-4b11-83ac-99f035fb9f8a" />

## How to run

**Prepare: Get Token**
https://qiita.com/tatsuki-tsuchiyama/items/fb15145029e5e7318bec

Run
```
$ make build
$ make dev
```

**1st step: Data Collection**
Run
```
$ make shell
$ python3 scripts/activity.py (receive json)
$ python3 convert.py (before received data move to convert.py)
```

**2nd Step: Display Data**
Access
```
http://localhost:8501/
```


