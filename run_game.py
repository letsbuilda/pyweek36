import sys

MIN_VER = (3, 10)

if sys.version_info[:2] >= MIN_VER:
    from pyweek36.main import main

    main()
else:
    sys.exit("This game requires Python {}.{}.".format(*MIN_VER))
