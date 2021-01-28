import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = " DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplay"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS times"

# CREATE TABLES

staging_events_table_create= ("""
                               CREATE TABLE staging_events(events_key   INTEGER IDENTITY(0,1) NOT NULL,
                                                           artist        VARCHAR,
                                                           auth          VARCHAR    NOT NULL,
                                                           firstName     VARCHAR,
                                                           gender        VARCHAR(1),
                                                           itemInSession INTEGER,
                                                           lastName      VARCHAR,
                                                           lenght        DECIMAL,
                                                           level         VARCHAR(4) NOT NULL,
                                                           location      VARCHAR,
                                                           method        VARCHAR(4) NOT NULL,
                                                           page          VARCHAR    NOT NULL,
                                                           registration  VARCHAR,
                                                           sessionId     INTEGER,
                                                           song          VARCHAR,
                                                           status        INTEGER,
                                                           ts            BIGINT     NOT NULL,
                                                           userAgent     VARCHAR,
                                                           userId        INTEGER 
                                                         )
                                                         """)

staging_songs_table_create = ("""
                               CREATE TABLE staging_songs(num_songs        INTEGER NOT NULL,
                                                          artist_id        VARCHAR NOT NULL,
                                                          artist_latitude  VARCHAR,
                                                          artist_longitude VARCHAR,
                                                          artist_location  VARCHAR,
                                                          artist_name      VARCHAR,
                                                          song_id          VARCHAR NOT NULL,
                                                          title            VARCHAR NOT NULL,
                                                          duration         DECIMAL NOT NULL,
                                                          year             INTEGER NOT NULL
                                                          )
                                                          """)

songplay_table_create = ("""
                          CREATE TABLE songplay(songplay_id   INTEGER IDENTITY(0,1) PRIMARY KEY NOT NULL,
                                                start_time    TIMESTAMP  NOT NULL sortkey,
                                                user_id       INTEGER,
                                                level         VARCHAR(4) NOT NULL,
                                                song_id       VARCHAR    NOT NULL distkey,
                                                artist_id     VARCHAR    NOT NULL,
                                                session_id    INTEGER,
                                                location      VARCHAR,
                                                user_agent    VARCHAR
                                                )
                                                """)

user_table_create = ("""
                      CREATE TABLE users(user_key   INTEGER IDENTITY(0,1) NOT NULL PRIMARY KEY,
                                         user_id    INTEGER  sortkey,
                                         first_name VARCHAR,
                                         last_name  VARCHAR,
                                         gender     VARCHAR(1),
                                         level      VARCHAR(4) NOT NULL
                                        )diststyle all
                                        """)

song_table_create = ("""
                      CREATE TABLE songs(song_id    VARCHAR NOT NULL PRIMARY KEY sortkey,
                                         title      VARCHAR NOT NULL,
                                         artist_id  VARCHAR NOT NULL,
                                         year       INTEGER NOT NULL,
                                         duration   DECIMAL NOT NULL
                                         )diststyle all
                                         """)

artist_table_create = ("""
                        CREATE TABLE artists(artist_id VARCHAR NOT NULL PRIMARY KEY sortkey,
                                             name      VARCHAR,
                                             location  VARCHAR,
                                             lattitude VARCHAR,
                                             longitude VARCHAR
                                             )diststyle all""")


time_table_create = ("""
                      CREATE TABLE times(ts         BIGINT NOT NULL PRIMARY KEY sortkey,
                                         start_time TIMESTAMP NOT NULL,
                                         hour       INTEGER NOT NULL,
                                         day        INTEGER NOT NULL,
                                         week       INTEGER NOT NULL,
                                         month      INTEGER NOT NULL,
                                         year       INTEGER NOT NULL,
                                         weekday    INTEGER NOT NULL
                                        )diststyle all
                                        """)
                                         

# STAGING TABLES

staging_events_copy = ("""
                        COPY staging_events FROM {}
                        CREDENTIALS 'aws_iam_role={}'
                        REGION 'us-west-2'
                        JSON {}
                        DATEFORMAT 'auto'
                        TIMEFORMAT 'auto';
                        """).format(config.get('S3','LOG_DATA'),config.get('IAM_ROLE','ARN'),config.get('S3','LOG_JSONPATH'))


staging_songs_copy = ("""COPY staging_songs FROM {}
                         CREDENTIALS 'aws_iam_role={}'
                         REGION 'us-west-2'
                         JSON 'auto';""").format(config.get('S3','SONG_DATA'),config.get('IAM_ROLE','ARN'))

# FINAL TABLES

songplay_table_insert = ("""INSERT INTO {}(artist_id,location,user_id,level,song_id,session_id,user_agent,start_time)
                            SELECT a.artist_id,s_event.location,s_event.userId,s_event.level,s.song_id,
                                 s_event.sessionId,  s_event.userAgent,
                                 TIMESTAMP WITHOUT TIME ZONE 'epoch' + (s_event.ts::bigint::float / 1000) * \
                                 INTERVAL '1 second' as start_time
                            FROM {} s_event
                            JOIN {} s ON (s_event.song = s.title AND s_event.lenght = s.duration)
                            JOIN {} a ON (s_event.artist = a.name)
                            WHERE page='NextSong' """).format('songplay','staging_events','songs','artists')

user_table_insert = ("""INSERT INTO {}(user_id,first_name,last_name,gender,level)
                        SELECT userId,firstName,lastName,gender,level
                        FROM {}""").format('users','staging_events')

song_table_insert = ("""INSERT INTO {}(song_id,title,artist_id,year,duration)
                        SELECT  song_id,title,artist_id,year,duration
                        FROM {}""").format('songs','staging_songs')

artist_table_insert = ("""INSERT INTO {}(artist_id,name,location,lattitude,longitude)
                          SELECT artist_id,artist_name,artist_location,artist_latitude,artist_longitude
                          FROM {}""").format('artists','staging_songs')

time_table_insert = ("""INSERT INTO {}(ts,start_time,hour,day,week,month,year,weekday)
                        SELECT s_events.ts as timestamp,
                             TIMESTAMP WITHOUT TIME ZONE 'epoch' + (s_events.ts::bigint::float / 1000) * INTERVAL '1 second' as start_time,
                             EXTRACT(hour  FROM TIMESTAMP WITHOUT TIME ZONE 'epoch' + (s_events.ts::bigint::float / 1000) * INTERVAL '1 second') as hour,
                             EXTRACT(day   FROM TIMESTAMP WITHOUT TIME ZONE 'epoch' + (s_events.ts::bigint::float / 1000) * INTERVAL '1 second') as day,
                             EXTRACT(week  FROM TIMESTAMP WITHOUT TIME ZONE 'epoch' + (s_events.ts::bigint::float / 1000) * INTERVAL '1 second') as week,
                             EXTRACT(month FROM TIMESTAMP WITHOUT TIME ZONE 'epoch' + (s_events.ts::bigint::float / 1000) * INTERVAL '1 second') as month,
                             EXTRACT(year  FROM TIMESTAMP WITHOUT TIME ZONE 'epoch' + (s_events.ts::bigint::float / 1000) * INTERVAL '1 second') as year,
                             EXTRACT(dow   FROM TIMESTAMP WITHOUT TIME ZONE 'epoch' + (s_events.ts::bigint::float / 1000) * INTERVAL '1 second') as weekday
                      FROM {} s_events""").format('times','staging_events')

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [user_table_insert, song_table_insert, artist_table_insert, time_table_insert,songplay_table_insert]
