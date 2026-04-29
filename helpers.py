import pathlib
async def create_data_folders():
    home_dir = pathlib.Path.home()
    base_dir = pathlib.Path('.count-von-count')
    bot_dir = pathlib.Path(home_dir).joinpath(base_dir)