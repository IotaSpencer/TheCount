import os
import json
import simpleeval
import sys

from sqlalchemy import select, Table, MetaData, inspect
from sqlalchemy.exc import NoSuchTableError

from models.base import Session, engine
from models.channels import Channels
from models.highscores import HighScores
from models.settings import Settings
from models.leaderboards import Leaderboards

from discord.ext.bridge import bridge_command

from config import Cfg
from logger import logger


class ChannelNotFoundError(Exception):
    """Raised when the channel is not registered."""

    pass


# Helper: attribute fallback for reflected ORM objects
def _attr_fallback(row, *names, default=None):
    for name in names:
        if hasattr(row, name):
            return getattr(row, name)
    try:
        for col in row.__table__.columns:
            if col.name in names:
                return getattr(row, col.name)
    except Exception:
        pass
    return default


def is_channel_registered(channelid):
    with Session() as session:
        return session.scalar(
            select(Channels).where(Channels.channelID == str(channelid))
        ) is not None


async def admin_check(ctx):
    # Support both context shapes used across the codebase
    try:
        author = ctx.message.author if getattr(ctx, 'message', None) else ctx.author
        if not author.guild_permissions.administrator:
            await ctx.reply("You're not an administrator, sorry!")
            return False
        return True
    except AttributeError:
        await ctx.reply("This command can only be used in a server.")
        return False


def get_channel_data(channelid, ForceIntegerConversions=True):
    with Session() as session:
        channel = session.scalar(
            select(Channels).where(Channels.channelID == str(channelid))
        )

        if channel is None:
            raise ChannelNotFoundError(f"Channel {channelid} is not registered")

        counter = _attr_fallback(channel, 'current_count', 'currentcount', 'counter', 'value', default=0)
        userid = _attr_fallback(channel, 'last_userID', 'lastUserID', 'last_user_id', 'lastuserid', default=0)
        timescounted = _attr_fallback(channel, 'times_counted', 'timescounted', 'times_count', 'timesCounted', default=0)

        if ForceIntegerConversions:
            return int(counter), int(userid), int(timescounted)

        return float(counter), int(userid), int(timescounted)


def set_channel_data(channelid, counter, userid, timescounted):
    with Session() as session:
        channel = session.scalar(
            select(Channels).where(Channels.channelID == str(channelid))
        )

        if channel is None:
            channel = Channels(channelID=str(channelid), serverID="0")
            try:
                setattr(channel, 'current_count', counter)
                setattr(channel, 'last_userID', str(userid))
                setattr(channel, 'times_counted', timescounted)
            except Exception:
                pass
            session.add(channel)
        else:
            for name, value in (
                ('current_count', counter),
                ('last_userID', str(userid)),
                ('times_counted', timescounted),
            ):
                try:
                    setattr(channel, name, value)
                except Exception:
                    pass

        session.commit()


def get_channel_highscore(channelid):
    with Session() as session:
        highscore = session.scalar(
            select(HighScores).where(HighScores.channelID == str(channelid))
        )

        if highscore is None:
            set_channel_highscore(channelid, 0)
            return 0

        return int(getattr(highscore, 'score', 0))


def set_channel_highscore(channelid, counter):
    with Session() as session:
        highscore = session.scalar(
            select(HighScores).where(HighScores.channelID == str(channelid))
        )

        if highscore is None:
            highscore = HighScores(
                channelID=str(channelid),
                serverID="0",
                score=counter,
            )
            session.add(highscore)
        else:
            try:
                setattr(highscore, 'score', counter)
            except Exception:
                pass

        session.commit()


def get_default_settings():
    # Prefer config count settings when available, otherwise fall back to sensible defaults.
    try:
        cfg = Cfg()
        if hasattr(cfg, 'count_config') and cfg.count_config is not None:
            try:
                return dict(cfg.count_config)
            except Exception:
                return {k: v for k, v in cfg.count_config.items()}
    except Exception:
        pass

    return {
        'Step': 1,
        'StartingNumber': 0,
        'EnableWolframAlpha': False,
        'EnableBinary': True,
        'EnableExpressions': True,
        'RoundAllGuesses': False,
        'AllowSingleUserCount': False,
        'ForceIntegerConversions': True,
    }


def get_channel_settings(channelid):
    defaults = get_default_settings()
    try:
        with Session() as session:
            settings_row = session.scalar(select(Settings).where(Settings.channelID == str(channelid)))
            if settings_row is None:
                return defaults

            rowdict = {}
            try:
                for col in settings_row.__table__.columns:
                    rowdict[col.name] = getattr(settings_row, col.name)
            except Exception:
                for attr in dir(settings_row):
                    if not attr.startswith('_'):
                        try:
                            rowdict[attr] = getattr(settings_row, attr)
                        except Exception:
                            pass

            out = defaults.copy()
            out.update(rowdict)
            return out
    except Exception as e:
        logger.debug(f'get_channel_settings using DB failed: {e}')
        return defaults


# Streak rankability: prefer a DB table when present, otherwise fall back to the existing file-backed behaviour.
def _ensure_streak_table():
    metadata = MetaData()
    try:
        if inspect(engine).has_table('streakrankability'):
            table = Table('streakrankability', metadata, autoload_with=engine)
            return table
    except Exception:
        pass
    return None


def get_channel_rankability(channelid):
    table = _ensure_streak_table()
    if table is not None:
        with Session() as session:
            try:
                if 'channelID' in table.c:
                    idcol = table.c.channelID
                elif 'channel_id' in table.c:
                    idcol = table.c.channel_id
                elif 'serverID' in table.c:
                    idcol = table.c.serverID
                else:
                    idcol = list(table.c)[0]

                sel = select(table).where(idcol == str(channelid))
                res = session.execute(sel).first()
                if res:
                    mapping = res._mapping if hasattr(res, '_mapping') else dict(res)
                    for key in ('rankable', 'rankability', 'value', 'is_rankable'):
                        if key in mapping:
                            try:
                                return bool(int(mapping[key]))
                            except Exception:
                                return bool(mapping[key])
                    for k, v in mapping.items():
                        if k != idcol.name:
                            try:
                                return bool(int(v))
                            except Exception:
                                pass
            except Exception as e:
                logger.debug(f'get_channel_rankability DB query failed: {e}')

    try:
        settings = get_channel_settings(channelid)
        for key in ('Rankable', 'rankable', 'is_rankable'):
            if key in settings:
                return bool(settings[key])
    except Exception:
        pass

    # No file fallback: return False when no DB-backed rankability found
    return False


def set_channel_rankability(channelid, rankability):
    table = _ensure_streak_table()
    if table is not None:
        with Session() as session:
            try:
                if 'channelID' in table.c:
                    idcol = table.c.channelID
                elif 'channel_id' in table.c:
                    idcol = table.c.channel_id
                else:
                    idcol = list(table.c)[0]

                sel = select(table).where(idcol == str(channelid))
                existing = session.execute(sel).first()

                # find flag column
                flag_col = None
                for name in ('rankable', 'rankability', 'is_rankable', 'value'):
                    if name in table.c:
                        flag_col = table.c[name]
                        break
                if flag_col is None:
                    cols = list(table.c)
                    if len(cols) > 1:
                        flag_col = cols[1]

                if existing:
                    upd = {flag_col.name: int(bool(rankability))} if flag_col is not None else {}
                    session.execute(table.update().where(idcol == str(channelid)).values(**upd))
                else:
                    insert_vals = {idcol.name: str(channelid)}
                    if flag_col is not None:
                        insert_vals[flag_col.name] = int(bool(rankability))
                    session.execute(table.insert().values(**insert_vals))

                session.commit()
                return
            except Exception as e:
                logger.debug(f'set_channel_rankability DB write failed: {e}')

    # If streakrankability table does not exist, raise so migrations can be applied
    raise RuntimeError('streakrankability table not found in DB; run migrations to create required tables')


def check_setting_rankability(channelid):
    return get_channel_settings(channelid) == get_default_settings()


def reset_channel_rankability(channelid):
    are_settings_rankable = check_setting_rankability(channelid)
    set_channel_rankability(channelid, are_settings_rankable)


def reset_streak(channelid):
    settings = get_channel_settings(channelid)
    starting = settings.get('StartingNumber', 0)
    set_channel_data(channelid, starting, 0, 0)
    reset_channel_rankability(channelid)


def reset_config(channelid):
    try:
        with Session() as session:
            settings_row = session.scalar(select(Settings).where(Settings.channelID == str(channelid)))
            if settings_row is not None:
                session.delete(settings_row)
                session.commit()
                return
    except Exception as e:
        logger.debug(f'reset_config DB delete failed: {e}')

    # If settings row was not present or DB delete failed, just log and continue.
    logger.debug(f'No settings row to delete for channel {channelid}')


def set_channel_setting(channelid, key, value):
    defaults = get_default_settings()
    if key not in defaults:
        raise KeyError("Setting not found")

    # Convert value to expected type
    valuetype = type(defaults[key])
    if valuetype in (int, float):
        number = float(value)
        if number.is_integer():
            number = int(number)
        converted = number
    elif valuetype == bool:
        converted = value.lower() in ["1", "true", "yes"] if isinstance(value, str) else bool(value)
    else:
        converted = value

    with Session() as session:
        settings_row = session.scalar(select(Settings).where(Settings.channelID == str(channelid)))
        if settings_row is None:
            settings_row = Settings(channelID=str(channelid))
            session.add(settings_row)

        try:
            setattr(settings_row, key, converted)
        except Exception as e:
            raise RuntimeError(f"Failed to set setting {key} on DB settings row: {e}")

        session.commit()


def remove_channel(channelid):
    with Session() as session:
        channel = session.scalar(select(Channels).where(Channels.channelID == str(channelid)))
        if channel is not None:
            session.delete(channel)
            session.commit()


def remove_channel_highscore(channelid):
    with Session() as session:
        hs = session.scalar(select(HighScores).where(HighScores.channelID == str(channelid)))
        if hs is not None:
            session.delete(hs)
            session.commit()


def remove_streak_rankability(channelid):
    table = _ensure_streak_table()
    if table is None:
        raise RuntimeError('streakrankability table not present in DB')
    with Session() as session:
        if 'channelID' in table.c:
            idcol = table.c.channelID
        elif 'channel_id' in table.c:
            idcol = table.c.channel_id
        else:
            idcol = list(table.c)[0]
        session.execute(table.delete().where(idcol == str(channelid)))
        session.commit()


def get_leaderboards():
    try:
        metadata = MetaData()
        if inspect(engine).has_table('leaderboards'):
            table = Table('leaderboards', metadata, autoload_with=engine)
            out = {'metadata': {}, 'scores': {}}
            with Session() as session:
                rows = session.execute(select(table)).all()
                if not rows:
                    return out
                scores = {}
                for row in rows:
                    mapping = row._mapping if hasattr(row, '_mapping') else dict(row)
                    channel_key = None
                    for key in ('channelID', 'channel_id', 'serverID', 'server_id'):
                        if key in mapping:
                            channel_key = key
                            break
                    if channel_key is None:
                        channel_key = list(mapping.keys())[0]
                    channelid = str(mapping[channel_key])
                    score = None
                    for key in ('score', 'value', 'points'):
                        if key in mapping:
                            score = mapping[key]
                            break
                    if score is None:
                        for k, v in mapping.items():
                            if k != channel_key and isinstance(v, (int, float)):
                                score = v
                                break
                    scores[channelid] = {
                        'name': mapping.get('name', ''),
                        'guildname': mapping.get('guildname', ''),
                        'score': int(score) if score is not None else 0
                    }
                out['scores'] = scores
                out['metadata']['lowest_leaderboard_score'] = min((v['score'] for v in scores.values()), default=0)
                return out
    except Exception as e:
        logger.debug(f'get_leaderboards DB fallback failed: {e}')

    # No file fallback: return empty leaderboard when DB query fails or table absent
    return {'metadata': {'lowest_leaderboard_score': 0}, 'scores': {}}


def set_leaderboards(data):
    try:
        metadata = MetaData()
        if inspect(engine).has_table('leaderboards'):
            table = Table('leaderboards', metadata, autoload_with=engine)
            with Session() as session:
                for channelid, info in data.get('scores', {}).items():
                    if 'channelID' in table.c:
                        idcol = table.c.channelID
                    elif 'channel_id' in table.c:
                        idcol = table.c.channel_id
                    elif 'serverID' in table.c:
                        idcol = table.c.serverID
                    else:
                        idcol = list(table.c)[0]
                    sel = select(table).where(idcol == str(channelid))
                    existing = session.execute(sel).first()
                    values = {}
                    for key in ('score', 'value', 'points'):
                        if key in table.c:
                            values[key] = int(info.get('score', 0))
                            break
                    for key in ('name',):
                        if key in table.c:
                            values[key] = info.get('name', '')
                    for key in ('guildname', 'guild_name'):
                        if key in table.c:
                            values[key] = info.get('guildname', '')
                    if existing:
                        session.execute(table.update().where(idcol == str(channelid)).values(**values))
                    else:
                        insert_vals = {idcol.name: str(channelid)}
                        insert_vals.update(values)
                        session.execute(table.insert().values(**insert_vals))
                session.commit()
                return
    except Exception as e:
        logger.debug(f'set_leaderboards DB write failed: {e}')
    raise RuntimeError('leaderboards table not present in DB; run migrations to create required tables')