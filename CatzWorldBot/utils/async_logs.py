import aiofiles
from utils.Constants import ConstantsClass

class LogMessageAsync:
    @staticmethod
    async def LogAsync(message, log_file=None):
        if log_file is None:
            log_file = ConstantsClass.get_github_project_directory() + '/CatzWorldBot/logs/catz_bot_logs.log'

        async with aiofiles.open(log_file, mode='a') as f:
            await f.write(f'{message}\n')
            print(f"Message logged: {message}") 

    @staticmethod
    async def reset_log_file(log_file=None):
        if log_file is None:
            log_file = ConstantsClass.get_github_project_directory() + '/CatzWorldBot/logs/catz_bot_logs.log'

        async with aiofiles.open(log_file, mode='w'):  # Open file in 'w' mode to truncate it
            pass  # The file is now empty
