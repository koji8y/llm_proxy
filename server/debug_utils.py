from datetime import datetime

def get_test_info_for_debug() -> dict[str, str]:
    return dict(test=f'{datetime.now().isoformat()}')
