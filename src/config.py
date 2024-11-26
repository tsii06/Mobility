DATABASE_CONFIG = {
    'dbname': 'boss',
    'user': 'postgres',
    'password': 'pronokeys06',
    'host': 'localhost',
    'port': '5432',
}


# def get_resource_usage():
#     pid = os.getpid()
#     process = psutil.Process(pid)
#     mem_info = process.memory_info()
#     cpu_usage = psutil.cpu_percent(interval=1)
#     print(f"CPU Usage: {cpu_usage}%")
#     print(f"Memory Usage: {mem_info.rss / 1024 ** 2} MB")