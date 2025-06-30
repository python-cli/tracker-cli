from datetime import datetime

def parse_time_str(strtime, default=datetime.now()):
    try:
        dt_obj = datetime.fromisoformat(strtime)
    except:
        dt_obj = None

    return dt_obj or default