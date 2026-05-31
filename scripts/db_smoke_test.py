#!/home/ken/.virtualenvs/TheCount/bin/python3.12
from uuid import uuid4
from sqlalchemy import inspect
from pathlib import Path
import sys

# Ensure project root is on sys.path so `models` package imports work when
# running this script from the `scripts/` directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.base import Session, engine
from models.channels import Channels
from models.highscores import HighScores
from models.settings import Settings
from models.leaderboards import Leaderboards
from models.personals import Personals
from models.streak_rankability import StreakRankability


def check_table(name: str) -> bool:
    return inspect(engine).has_table(name)


def run_test() -> int:
    print('Starting DB smoke test')
    required = ['channels', 'highscores', 'settings', 'leaderboards', 'personals', 'streakrankability']
    missing = [t for t in required if not check_table(t)]
    if missing:
        print('Missing tables:', missing)
        return 2

    test_channel = f'smoketest_{uuid4().hex[:8]}'
    test_user = f'user_{uuid4().hex[:8]}'
    print('Using test channel:', test_channel)

    try:
        with Session() as s:
            # Insert
            c = Channels(channelID=test_channel, serverID='srv', current_count=42, last_userID=test_user, times_counted=7)
            h = HighScores(channelID=test_channel, serverID='srv', score=100)
            st = Settings(channelID=test_channel, Step=1, StartingNumber=0)
            lb = Leaderboards(channelID=test_channel, serverID='srv', name='Test LB', guildname='Test Guild', score=200)
            p = Personals(userID=test_user, correct_count=5, incorrect_count=2)
            sr = StreakRankability(channelID=test_channel, rankable=1)

            s.add_all([c, h, st, lb, p, sr])
            s.commit()
            print('Insert: OK')

            # Read
            got_c = s.get(Channels, test_channel)
            got_h = s.get(HighScores, test_channel)
            got_st = s.get(Settings, test_channel)
            got_lb = s.get(Leaderboards, test_channel)
            got_p = s.get(Personals, test_user)
            got_sr = s.get(StreakRankability, test_channel)

            print('Read Channels:', got_c)
            print('Read HighScores:', got_h)
            print('Read Settings:', got_st)
            print('Read Leaderboards:', got_lb)
            print('Read Personals:', got_p)
            print('Read StreakRankability:', got_sr)

            # Update
            got_c.current_count = 99
            if got_h:
                got_h.score = 150
            if got_lb:
                got_lb.score = 250
            if got_p:
                got_p.correct_count = 10
            s.commit()
            print('Update: OK')

            # Cleanup
            for obj in (got_c, got_h, got_st, got_lb, got_p, got_sr):
                try:
                    if obj is not None:
                        s.delete(obj)
                except Exception:
                    pass
            s.commit()
            print('Delete: OK')
    except Exception as e:
        print('Smoke test failed:', repr(e))
        return 1

    print('DB smoke test completed successfully')
    return 0


if __name__ == '__main__':
    raise SystemExit(run_test())
