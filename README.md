# app-monitor

## Use docker-compose to run all containers
```bash
# normal startup
docker compose up -d

# startup if there are changes
docker compose up -d --build
```

## View Logs in mysql
```bash
docker exec -it mysql-container mysql -u root -p
```
```sql
use log_monitoring;
select * from logs limit 50;
```

## view metrics on prometheus
```bash
http://localhost:9090

Try querying:
    api_requests_total
    api_responses_total
    api_errors_total
    api_response_time_seconds_bucket
```

## Access Grafana Dashboard
```bash
http://localhost:3001
```

Login with:
- **Username**: `admin`
- **Password**: `admin`
