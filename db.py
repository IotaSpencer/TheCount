import sqlalchemy
from models import
from models.channels import Channels


def get_channel_data(self, channelid, ForceIntegerConversions=True):
    with open("channels/" + str(channelid), "r") as file:
        data = file.read().split("|")
        if ForceIntegerConversions:
            return int(data[0]), int(data[1]), int(data[2])
        else:
            return float(data[0]), int(data[1]), int(data[2])


def set_channel_data(self, channelid, counter, userid, timescounted):
    with open("channels/" + str(channelid), "w") as file:
        file.write(f"{counter}|{userid}|{timescounted}")


def get_channel_highscore(self, channelid):
    with open("highscores/" + str(channelid), "r") as file:
        Channels
        return int(file.read())


def set_channel_highscore(self, channelid, counter):
    with open("highscores/" + str(channelid), "w") as file:
        file.write(f"{counter}")


def get_default_settings(self):
    with open("settings/default.json", "r") as file:
        return json.load(file)


def get_channel_settings(self, channelid):
    filepath = "settings/" + str(channelid) + ".json"
    if not os.path.exists(filepath):
        filepath = "settings/default.json"
    settings = self.get_default_settings()
    with open(filepath, "r") as file:
        settings.update(json.load(file))
        return settings


def set_channel_setting(self, channelid, key, value):
    if value.lower().removeprefix("-") in ("nan", "inf", "infinity"):
        raise ValueError("No.")
    filepath = "settings/" + str(channelid) + ".json"
    if not os.path.exists(filepath):
        filepath = "settings/default.json"
    with open(filepath, "r") as file:
        settings = json.load(file)
    defaultsettings = self.get_default_settings()
    if not key in defaultsettings.keys():
        raise KeyError("Setting not found")
    writepath = "settings/" + str(channelid) + ".json"
    valuetype = type(defaultsettings[key])
    if valuetype in (int, float):
        number = float(value)
        if number.is_integer():
            number = int(number)
        settings.update({key: number})
    elif valuetype == bool:
        istrue = value.lower() in ["1", "true", "yes"]
        settings.update({key: istrue})
    else:  # str & others
        settings.update({key: value})
    filepath = "settings/" + str(channelid) + ".json"
    with open(filepath, "w") as file:
        return json.dump(settings, file)


def get_channel_rankability(self, channelid):
    try:
        with open("streakrankability/" + str(channelid), "r") as file:
            return bool(int(file.read()))
    except FileNotFoundError:
        self.set_channel_rankability(channelid, False)
        return False


def set_channel_rankability(self, channelid, rankability):
    with open("streakrankability/" + str(channelid), "w") as file:
        file.write(str(int(rankability)))


def check_setting_rankability(self, channelid):
    return self.get_channel_settings(channelid) == self.get_default_settings()


def reset_channel_rankability(self, channelid):
    are_settings_rankable = self.check_setting_rankability(channelid)
    self.set_channel_rankability(channelid, are_settings_rankable)


def reset_streak(self, channelid):
    settings = self.get_channel_settings(channelid)
    self.set_channel_data(channelid, settings["StartingNumber"], 0, 0)
    self.reset_channel_rankability(channelid)


def reset_config(self, channelid):
    try:
        os.remove("settings/" + str(channelid) + ".json")
    except FileNotFoundError:
        pass


def get_leaderboards(self):
    with open("leaderboards.json", "r") as file:
        return json.load(file)


def set_leaderboards(self, data):
    with open("leaderboards.json", "w") as file:
        return json.dump(data, file)